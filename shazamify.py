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
        next(reader)
        next(reader)
        next(reader)
        
        # Read the remaining rows, keeping only columns 2 and 3
        tracks = [[row[1], row[2]] for row in reader if len(row) >= 3]
    return tracks

# Function for fuzzy matching
def fuzzy_match(query, choices, threshold=80):
    return [(choice, score) for choice in choices if (score := fuzz.partial_ratio(query, choice)) >= threshold]

# Function to check if a track was released in 2023
def is_track_released_in_2023(track_uri):
    track_info = sp.track(track_uri)
    release_date = track_info['album']['release_date']
    return release_date.startswith('2023')

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

        # Search for the track on Spotify
        search_query = f"{artist} {title}"
        search_results = sp.search(q=search_query, type='track', limit=1)

        if search_results['tracks']['items']:
            result = search_results['tracks']['items'][0]
            result_artist = result['artists'][0]['name']
            result_title = result['name']
            result_uri = result['uri']

            # Check if the song was released in 2023
            if is_track_released_in_2023(result_uri):
                # Check for duplicates
                existing_tracks = sp.playlist_tracks(SPOTIFY_PLAYLIST_ID)['items']
                duplicate_check = any(track['track']['uri'] == result_uri for track in existing_tracks)

                if duplicate_check:
                    print(f"Skipped (Duplicate): {result_title} by {result_artist}")
                    tracks_skipped_duplicate += 1
                else:
                    sp.playlist_add_items(SPOTIFY_PLAYLIST_ID, [result_uri])
                    print(f"Added: {result_title} by {result_artist}")
                    tracks_added += 1
            else:
                print(f"Skipped (Not released in 2023): {result_title} by {result_artist}")
                tracks_skipped_wrong_year += 1
        else:
            print(f"Skipped (Not found): {title} by {artist}")
            tracks_skipped_not_found += 1

# Print summary
print("\nSummary:")
print(f"Tracks Added: {tracks_added}")
print(f"Tracks Skipped (Duplicate): {tracks_skipped_duplicate}")
print(f"Tracks Skipped (Wrong year): {tracks_skipped_wrong_year}")
print(f"Tracks Skipped (Not Found): {tracks_skipped_not_found}")
