# shazamify
Automatically get songs from Shazam's Charts and pipe them into a Spotify Playlist. Download the Python scripts, edit the CSV and Authorisation variables, and run them in terminal (Python required) or Python Launcher.

Currently, the script is set up so as to ignore duplicate songs as well as songs that aren't from 2023. The hope is to start these in 2024 on a weekly cron job and have a cumulative list of tracks over the year.

# How to use the scripts

## Set up your Spotify Dev account here using these instructions
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
