import os
import re
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import VideosSearch
from pytube import YouTube

SPOTIPY_CLIENT_ID = #[YOUR CLIENT ID]
SPOTIPY_CLIENT_SECRET = #[YOUR CLIENT SECRET]

client_credentials_manager = SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
def validate_url(sp_url):
    if re.search(r"^(https?://)?open\.spotify\.com/playlist/.+$", sp_url):
        return sp_url
    raise ValueError("Invalid Spotify Playlist URL")
def get_playlist_info(sp_playlist):
    res = requests.get(sp_playlist)
    if res.status_code != 200:
        raise ValueError("Invalid Spotify playlist URL")
    pl = sp.playlist(sp_playlist)
    if not pl["public"]:
        raise ValueError("Can't access private playlists. Make sure your playlist is public.")
    playlist = sp.playlist_tracks(sp_playlist)
    tracks = [item["track"] for item in playlist["items"]]
    tracks_info = []
    for track in tracks:
        track_info = {
            "artist_name": track["artists"][0]["name"],
            "track_title": track["name"],
        }
        tracks_info.append(track_info)
    return tracks_info

if __name__ == "__main__":
    playlist_url = validate_url(input("Enter a Spotify playlist URL: ").strip())
    tracks = get_playlist_info(playlist_url)
    download_folder = "downloads"
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    name = input("tell me the name of the folder: ")
    for i, track_info in enumerate(tracks, start=1):
        # Uncomment the following lines to get the YouTube video URL for each track
        search_query = f"{track_info['artist_name']} - {track_info['track_title']}"
        videos_search = VideosSearch(search_query, limit=1)
        videos_result = videos_search.result()
        video_url = videos_result['result'][0]['link']
        url = video_url
        try:
            video = YouTube(url)
            stream = video.streams.filter(only_audio=True).first()
            filename = f"{track_info['artist_name']} - {track_info['track_title']}.mp3"
            filepath = os.path.join(name, filename)
            stream.download(output_path=name, filename=f"{video.title}.mp3")
            print(f"{filename} is downloaded")


        except KeyError:
            print("Unable to get the info!!")
print(f"your playlist is downloaded in {name}")
