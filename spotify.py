import os
import re
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import VideosSearch
from pytube import YouTube
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QFileDialog,
)
import configparser

CONFIG_FILE = "config.ini"

class PlaylistDownloaderApp(QWidget):
    def __init__(self):
        super().__init__()

        self.client_id = ""
        self.client_secret = ""

        self.load_credentials()
        self.init_ui()

    def load_credentials(self):
        config = configparser.ConfigParser()
        if os.path.exists(CONFIG_FILE):
            config.read(CONFIG_FILE)
            self.client_id = config.get("Spotify", "ClientID", fallback="")
            self.client_secret = config.get("Spotify", "ClientSecret", fallback="")

    def save_credentials(self):
        config = configparser.ConfigParser()
        config["Spotify"] = {"ClientID": self.client_id, "ClientSecret": self.client_secret}
        with open(CONFIG_FILE, "w") as configfile:
            config.write(configfile)

    def init_ui(self):
        self.setWindowTitle("Playlist Downloader")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        # Spotify Client ID
        self.client_id_label = QLabel("Enter Spotify Client ID:")
        self.client_id_entry = QLineEdit(self)
        self.client_id_entry.setText(self.client_id)
        layout.addWidget(self.client_id_label)
        layout.addWidget(self.client_id_entry)

        # Spotify Client Secret
        self.client_secret_label = QLabel("Enter Spotify Client Secret:")
        self.client_secret_entry = QLineEdit(self)
        self.client_secret_entry.setText(self.client_secret)
        layout.addWidget(self.client_secret_label)
        layout.addWidget(self.client_secret_entry)

        # Playlist URL
        self.playlist_label = QLabel("Enter Spotify Playlist URL:")
        self.playlist_url_entry = QLineEdit(self)
        layout.addWidget(self.playlist_label)
        layout.addWidget(self.playlist_url_entry)

        # Download Folder
        self.folder_label = QLabel("Select Download Folder:")
        self.folder_entry = QLineEdit(self)
        self.browse_button = QPushButton("Browse", self)
        self.browse_button.clicked.connect(self.browse_folder)
        layout.addWidget(self.folder_label)
        layout.addWidget(self.folder_entry)
        layout.addWidget(self.browse_button)

        # Download Button
        self.download_button = QPushButton("Start Download", self)
        self.download_button.clicked.connect(self.start_download)
        layout.addWidget(self.download_button)

        self.setLayout(layout)

    def browse_folder(self):
        folder_selected = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        self.folder_entry.setText(folder_selected)

    def validate_url(self, sp_url):
        if re.search(r"^(https?://)?open\.spotify\.com/playlist/.+$", sp_url):
            return sp_url
        raise ValueError("Invalid Spotify Playlist URL")

    def get_playlist_info(self, sp_playlist):
        auth_manager = SpotifyClientCredentials(
            client_id=self.client_id, client_secret=self.client_secret
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)

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

    
    def download_tracks(self, playlist_url, download_folder):
        tracks = self.get_playlist_info(playlist_url)

        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

        for i, track_info in enumerate(tracks, start=1):
            search_query = f"{track_info['artist_name']} - {track_info['track_title']}"
            videos_search = VideosSearch(search_query, limit=1)
            videos_result = videos_search.result()
            video_url = videos_result["result"][0]["link"]
            url = video_url
            try:
                video = YouTube(url)
                stream = video.streams.filter(only_audio=True).first()

                # Fixing file path and handling invalid characters in the filename
                filename = f"{track_info['artist_name']} - {track_info['track_title']}.mp3"
                filename = re.sub(r'[\\/:*?"<>|]', '_', filename)  # Replace invalid characters
                filepath = os.path.join(download_folder, filename)

                stream.download(output_path=download_folder, filename=filename)
                print(f"{filename} is downloaded")
            except KeyError:
                print("Unable to get the info!!")

    
    def start_download(self):
        self.client_id = self.client_id_entry.text().strip()
        self.client_secret = self.client_secret_entry.text().strip()
        self.save_credentials()
        playlist_url = self.validate_url(self.playlist_url_entry.text().strip())
        download_folder = self.folder_entry.text()
        self.download_tracks(playlist_url, download_folder)

if __name__ == "__main__":
    app = QApplication([])
    window = PlaylistDownloaderApp()
    window.show()
    app.exec_()
