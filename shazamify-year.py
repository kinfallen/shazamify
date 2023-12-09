import os
import requests
import csv
from fuzzywuzzy import fuzz
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Constants (REPLACE url)
url = "https://www.shazam.com/services/charts/csv/discovery/australia/"
local_folder = "/Users/You/Documents/Path/"
file_name = "file.csv"
local_path = os.path.join(local_folder, file_name)

# Spotify API credentials
SPOTIPY_CLIENT_ID = "clientID"
SPOTIPY_CLIENT_SECRET = "clientSecret"
SPOTIPY_REDIRECT_URI = "http://localhost:8888/callback"
SPOTIPY_USERNAME = "spotifyUsername"
SPOTIFY_PLAYLIST_ID = "playlistID"

# Function to download the CSV file
def download_csv_file(url, local_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(local_path, 'wb') as f:
            f.write(response.content)
        print(f"CSV file downloaded successfully to: {local_path}")
    else:
        raise Exception(f"Error downloading CSV file: {response.status_code}")

# Function to process the CSV file and filter columns
def process_csv_file(local_path):
    with open(local_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        # Skip the first three rows
        for _ in range(3):
            next(reader)
        
        # Read the remaining rows, keeping only columns 2 and 3
        tracks = [[row[1], row[2]] for row in reader if len(row) >= 3]
    return tracks

# Function to search for tracks on Spotify with fuzzy matching using fuzz
def search_spotify_with_fuzzy(query, sp, threshold=0.8):
    results = sp.search(q=query, type='track', limit=1)

    if 'items' in results['tracks']:
        # Filter tracks based on fuzzy matching
        tracks = results['tracks']['items']
        fuzzy_matches = [(track, fuzzy_match(query, [f"{track['artists'][0]['name']} {track['name']}"], threshold)) for track in tracks]

        # Return tracks with fuzzy matches
        return [track for track, matches in fuzzy_matches if any(matches)]
    else:
        return []

# Function to search for tracks on Spotify without fuzzy matching
def search_spotify(query, sp):
    results = sp.search(q=query, type='track', limit=1)

    if 'items' in results['tracks']:
        return results['tracks']['items']
    else:
        return []

# Function for fuzzy matching using fuzz
def fuzzy_match(query, choices, threshold=0.8):
    matches = []

    for choice in choices:
        similarity_ratio = fuzz.token_sort_ratio(query, choice)

        if similarity_ratio >= threshold:
            matches.append((choice, similarity_ratio))

    return matches

# Function to check if a track is released in 2023
def is_track_released_in_2023(track_uri):
    track_info = sp.track(track_uri)
    release_date = track_info['album']['release_date']
    return release_date.startswith('2023')

# Function to check for duplicates
def is_track_duplicate(track, existing_tracks, sp):
    result_uri = track['uri']

    # Step 1: Check for exact URI match
    print("------- Checking for exact URI match -------")
    for existing_track in existing_tracks:
        if existing_track['track']['uri'] == result_uri:
            print(f"  **Found exact match by URI:**")
            print(f"    - Existing track URI: {existing_track['track']['uri']}")
            print(f"    - Result track URI: {result_uri}")
            return True, None, None
        else:
            print(f"  - Comparing with existing track URI: {existing_track['track']['uri']}")
    print("  **No exact URI match found.**")

    # Step 2: If no URI match, do an exact artist and title match
    print("------- Checking for exact artist and title match -------")

    # Check if the exact match is already in the playlist
    is_exact_match_in_playlist = any(existing_track['track']['uri'] == result_uri for existing_track in existing_tracks)
    print(f"Is exact match in playlist: {is_exact_match_in_playlist}")

    if not is_exact_match_in_playlist:
        search_query = f"{track['artists'][0]['name']} {track['name']}"
        results = sp.search(q=search_query, type='track', limit=1)
        exact_match_results = results['tracks']['items']

        if exact_match_results:
            exact_match = exact_match_results[0]
            exact_match_uri = exact_match['uri']

            if (
                exact_match['artists'][0]['name'] == track['artists'][0]['name']
                and exact_match['name'] == track['name']
                and exact_match['uri'] != track['uri']
                and exact_match['id'] != track['id']
            ):
                print("  **Found exact match by artist and title:**")
                print(f"    - Existing artist: {exact_match['artists'][0]['name']}")
                print(f"    - Existing title: {exact_match['name']}")
                print(f"    - Existing URI: {exact_match_uri}")
                print(f"    - Result artist: {track['artists'][0]['name']}")
                print(f"    - Result title: {track['name']}")
                print(f"    - Result URI: {result_uri}")
                return True, None, None

    # If no exact match is found, check for fuzzy matches
    print(f"  **No exact match found for artist and title. Checking for fuzzy match.**")
    fuzzy_match_artist, fuzzy_match_title = check_for_fuzzy_match(track, existing_tracks, sp)
    if fuzzy_match_artist is not None and fuzzy_match_title is not None:
        if any(fuzzy_match_artist) and any(fuzzy_match_title):
            print(f"  **Found fuzzy match for artist and title.**")
            return True, fuzzy_match_artist, fuzzy_match_title

    return False, None, None

# Function to check for fuzzy matches
def check_for_fuzzy_match(track, existing_tracks, sp):
    fuzzy_match_artist = []
    fuzzy_match_title = []

    for existing_track in existing_tracks:
        if (
            existing_track['track']['artists'][0]['name'] == track['artists'][0]['name']
            and fuzz.token_sort_ratio(existing_track['track']['name'], track['name']) >= 80  # You can adjust the threshold
        ):
            fuzzy_match_artist.append(existing_track['track']['artists'][0]['name'])
            fuzzy_match_title.append(existing_track['track']['name'])
            print(f"    - Existing artist: {existing_track['track']['artists'][0]['name']}")
            print(f"    - Existing title: {existing_track['track']['name']}")
            print(f"    - Result artist: {track['artists'][0]['name']}")
            print(f"    - Result title: {track['name']}")

    return fuzzy_match_artist, fuzzy_match_title


# Spotify authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    username=SPOTIPY_USERNAME,
    scope="playlist-modify-public"
))

# Download the CSV file
download_csv_file(url, local_path)

# Process the CSV file
tracks_from_csv = process_csv_file(local_path)

# Add tracks to Spotify playlist
tracks_added = 0
tracks_skipped_duplicate = 0
tracks_skipped_wrong_year = 0
tracks_skipped_not_found = 0

# Process tracks in batches
batch_size = 100
for i in range(0, len(tracks_from_csv), batch_size):
    batch = tracks_from_csv[i:i + batch_size]

for track in batch:
    artist, title = track

    # Use a separate variable for the search query
    search_query = f"{artist} {title}"

    # Print raw track information
    print(f"\nSearching for: {title} by {artist}")

    # Search for the track on Spotify with exact match
    exact_match_results = search_spotify(search_query, sp)

    if exact_match_results:
        result = exact_match_results[0]
        result_artist = result['artists'][0]['name']
        result_title = result['name']
        print(f'Found "{result_title} by {result_artist}" in Spotify with exact match')
        print(f"Is exact match in playlist: False")  # Update this line based on the actual logic
        result_uri = result['uri']
        if is_track_released_in_2023(result_uri):
            existing_tracks = sp.playlist_tracks(SPOTIFY_PLAYLIST_ID)['items']
            duplicate_check, fuzzy_match_artist, fuzzy_match_title = is_track_duplicate(result, existing_tracks, sp)

            if duplicate_check:
                if fuzzy_match_artist is not None and fuzzy_match_title is not None:
                    if any(fuzzy_match_artist) and any(fuzzy_match_title):
                        print(f"Is a Fuzzy Match: {fuzzy_match_artist[0]} - {fuzzy_match_title[0]}")
                        print(f"Skipped (Fuzzy match): {result_title} by {result_artist}")
                    else:
                        # Include additional logic to identify the reason
                        print(f"Is a Fuzzy Match: None")
                        print(f"Skipped (Duplicate - Reason unknown): {result_title} by {result_artist}")
                    tracks_skipped_duplicate += 1
                else:
                    # Handle the case where fuzzy_match_artist or fuzzy_match_title is None
                    print(f"Is a Fuzzy Match: None")
                    print(f"Skipped (Duplicate - Fuzzy match details not available): {result_title} by {result_artist}")
            else:
                sp.playlist_add_items(SPOTIFY_PLAYLIST_ID, [result_uri])
                tracks_added += 1

            # Continue to the next track in the batch
            continue

    # If exact match not found, try fuzzy matching
    fuzzy_match_results = search_spotify_with_fuzzy(search_query, sp)

    if fuzzy_match_results:
        result = fuzzy_match_results[0]
        result_artist = result['artists'][0]['name']
        result_title = result['name']
        print(f'Found "{result_title} by {result_artist}" in Spotify with fuzzy match')
    else:
        print(f"Skipped (Not found): {title} by {artist}")
        tracks_skipped_not_found += 1
        continue

    result_uri = result['uri']

    # Check if the song was released in 2023
    if is_track_released_in_2023(result_uri):

        # Check for duplicates
        existing_tracks = sp.playlist_tracks(SPOTIFY_PLAYLIST_ID)['items']
        duplicate_check, fuzzy_match_artist, fuzzy_match_title = is_track_duplicate(result, existing_tracks, sp)

        if duplicate_check:
            if fuzzy_match_artist is not None and fuzzy_match_title is not None:
                if any(fuzzy_match_artist) and any(fuzzy_match_title):
                    print(f"Is a Fuzzy Match: {fuzzy_match_artist[0]} - {fuzzy_match_title[0]}")
                    print(f"Skipped (Fuzzy match): {result_title} by {result_artist}")
                else:
                    # Include additional logic to identify the reason
                    print(f"Is a Fuzzy Match: None")
                    print(f"Skipped (Duplicate - Reason unknown): {result_title} by {result_artist}")
                tracks_skipped_duplicate += 1
            else:
                # Handle the case where fuzzy_match_artist or fuzzy_match_title is None
                print(f"Is a Fuzzy Match: None")
                print(f"Skipped (Duplicate - Fuzzy match details not available): {result_title} by {result_artist}")
        else:
            sp.playlist_add_items(SPOTIFY_PLAYLIST_ID, [result_uri])
            print(f"Added to playlist")
            tracks_added += 1

# Print summary
playlist_info = sp.playlist(SPOTIFY_PLAYLIST_ID)
playlist_name = playlist_info['name']
print("\nSummary:")
print(f"{tracks_added} tracks added to the Spotitfy playlist: {playlist_name}")
print(f"Tracks Skipped (Duplicate): {tracks_skipped_duplicate}")
print(f"Tracks Skipped (Wrong year): {tracks_skipped_wrong_year}")
print(f"Tracks Skipped (Not Found): {tracks_skipped_not_found}")
