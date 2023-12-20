import csv
import os
from dotenv import load_dotenv

class Playlist:
    def __init__(self, name, image, songs):
        self.name = name
        self.image = image
        self.songs = songs

class Song:
    def __init__(self, name, artist, popularity, audio, image, playlist):
        self.name = name
        self.artist = artist
        self.popularity = popularity
        self.audio = audio
        self.image = image
        self.playlist = playlist

# Read a single song
def read_song(song, playlist_name):
    song_name = song[0]
    song_artist = song[1]
    song_popularity = song[2]
    song_audio = song[3]
    song_image = song[4]
    song_playlist = playlist_name

    new_song = Song(song_name, song_artist, song_popularity, song_audio, song_image, song_playlist)

    return new_song

# Read all songs in a playlist
def read_songs(songs_path, playlist_name):
    with open(songs_path, "r", encoding="utf-8") as song_file:
        song_reader = csv.reader(song_file)

        next(song_reader)

        songs = []

        for song in song_reader:
            if song[5] == playlist_name:
                new_song = read_song(song, playlist_name)
                songs.append(new_song)

    return songs

# Read a playlist
def read_playlist(playlist, songs_path):
    playlist_name = playlist[0]
    playlist_image = playlist[1]
    playlist_songs = read_songs(songs_path, playlist_name)

    playlist = Playlist(playlist_name, playlist_image, playlist_songs)

    return playlist

# Read all playlists
def read_playlists():
    # The reason I do not read the env file from beginning is because it is said to not use global variable
    load_dotenv()
    playlists_path = os.getenv("playlists_path", "")
    songs_path = os.getenv("songs_path", "")

    playlists = []

    with open(playlists_path, "r", encoding="utf-8") as playlist_file:
        playlist_reader = csv.reader(playlist_file)

        next(playlist_reader)

        for playlist in playlist_reader:
            new_playlist = read_playlist(playlist, songs_path)
            playlists.append(new_playlist)

    return playlists

def read_users():
    users = []
    with open("../Record/users.txt", "r", encoding="utf-8") as file:
        for line in file.readlines():
            users.append(line.strip())

    return users