# shazamify
Automatically get songs from Shazam's Charts and pipe them into a Spotify Playlist


# Set up your Spotify Dev account here using these instructions
https://developer.spotify.com/documentation/web-api/tutorials/getting-started

# Constants 
### Get the URL for the chart you want from the [Shazam Chart website](https://www.shazam.com/charts/top-200/australia)

	url = "https://www.shazam.com/services/charts/csv/top-200/australia/"

### Local path to store the CSV

	local_folder = "/Users/You/Documents/Path/"

### Call it something

	file_name = "file.csv"

# Spotify API credentials

### Client and secret from your Spoify Dev account page

	SPOTIPY_CLIENT_ID = "clientId"
	SPOTIPY_CLIENT_SECRET = "clientSecret"

### Use this URL

	SPOTIPY_REDIRECT_URI = "http://localhost:8888/callback"

### Spotify username

	SPOTIPY_USERNAME = "spotifyUser"

### Playlist ID (easy to get from viewing the playlist on Spotify web)

	SPOTIFY_PLAYLIST_ID = "playlistID"


# Caveats
	scope="playlist-modify-public" 
will only work if the playlist is actually public. Empty playlists start as private so use:

	scope="playlist-modify-private"
for the first run
