import csv
import os
import re
import subprocess
import json
import requests
import spotipy
from PIL import Image
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

# This function is used to redirect command
def subprocess_command(wanted_path, command):
    os.chdir(wanted_path)
    subprocess.run(command, shell=True, check=True)
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

# This function is used to download image by url
def get_image(url, playlist_path, name, image_width, image_height):
    data = requests.get(url).content

    image_path = f"{playlist_path}/{name}.jpg"
    with open(image_path, "wb") as file:
        file.write(data)

    image = Image.open(image_path)
    resized_image = image.resize((image_width, image_height))
    resized_image.save(image_path)

    return image_path

# This function is used to download song by url
def get_song(url, parent_path, file_name):
    command = f"mkdir \"{file_name}\""
    subprocess_command(parent_path, command)

    location = f"{parent_path}/{file_name}"
    command = f"spotdl {url}"
    subprocess_command(location, command)
    
    song_audio_path = None
    if os.path.exists(f"{parent_path}/{file_name}"):
        with os.scandir(f"{parent_path}/{file_name}") as entries:
            for entry in entries:
                if entry.is_file() and entry.name.lower().endswith('.mp3'):
                    song_audio_path = f"{parent_path}/{file_name}/{entry.name}"

    return song_audio_path

# This function is used to write new row to a csv file
def write_to_csv_file(file, mode, content):
    with open(file, mode, encoding = "utf-8", newline = "") as file:
        writer = csv.writer(file)
        writer.writerow(content)

# This function is used to clean a name
def clean_file_name(name):
    cleaned_name = re.sub(r'[<>:"/\\|?*]|(\.\.)', '', name)
    return cleaned_name

# This function is used to download a Spotify playlist
def get_playlist(playlist_link):
    # Get client id and secret id from .env file
    load_dotenv()
    client_ID = os.getenv("client_ID", "")
    client_secret = os.getenv("client_secret", "")
    data_path = os.getenv("data_path", "")
    record_path = os.getenv("record_path", "")

    # Get data for playlist
    client_credentials_manager = SpotifyClientCredentials(client_ID, client_secret)
    session = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    playlist_uri_match = re.search(r"https://open.spotify.com/playlist/([a-zA-Z0-9]+)", playlist_link)

    playlist = session.playlist(playlist_link)

    # Get playlist information
    playlist_name = clean_file_name(playlist["name"])

    create_playlist_path_command = f"mkdir \"{playlist_name}\""
    subprocess_command(data_path, create_playlist_path_command)
    playlist_path = f"{data_path}/{playlist_name}"

    playlist_image_url = playlist["images"][0]["url"]
    playlist_image = get_image(playlist_image_url, playlist_path, playlist_name, 200, 200)

    playlist_information = [playlist_name, playlist_image, playlist_path]
    playlist_record_path = f"{record_path}/playlists.csv"

    # Write playlist information to file
    write_to_csv_file(playlist_record_path, "a", playlist_information)
        
    # Download song and get song info
    songs = playlist["tracks"]["items"]
    for i in range(len(songs)):
        song_name = clean_file_name(songs[i]["track"]["name"])
        song_id = songs[i]["track"]["id"]
        song_url = f"https://open.spotify.com/track/{song_id}"
        song_audio = get_song(song_url, playlist_path, song_name)

        if song_audio != None: # File only be written if the song is downloadable

            song_artist = songs[i]["track"]["artists"][0]["name"]
            song_popularity = songs[i]["track"]["popularity"]

            song_image_url = songs[i]["track"]["album"]["images"][0]["url"]
            song_location = f"{playlist_path}/{song_name}" 
            song_image = get_image(song_image_url, song_location, song_name, 200, 200)

            song_information = [song_name, song_artist, song_popularity, song_audio, song_image, playlist_name]

            song_record_path = f"{record_path}/songs.csv"

            # Write song info to file
            write_to_csv_file(song_record_path, "a", song_information)

def get_a_single_song(song_link, playlist_name, songs_in_playlist):
    # Get client id and secret id from .env file
    load_dotenv()
    client_ID = os.getenv("client_ID", "")
    client_secret = os.getenv("client_secret", "")
    data_path = os.getenv("data_path", "")
    record_path = os.getenv("record_path", "")

    # Get song information
    client_credentials_manager = SpotifyClientCredentials(client_ID, client_secret)
    session = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    song = session.track(song_link)

    song_name = clean_file_name(song["name"])
    # Check if song is in playlist or not
    exist = False
    for song_in in songs_in_playlist:
        if song_in.name == song_name:
            exist = True
            return exist
        
    if exist == False:
        # Download song
        song_id = song["id"]
        song_url = f"https://open.spotify.com/track/{song_id}"
        playlist_path = f"../Data/{playlist_name}"
        song_audio = get_song(song_url, playlist_path, song_name)

        if song_audio != None:
            song_location = f"{playlist_path}/{song_name}"
            song_image_url = song["album"]["images"][0]["url"]
            song_artist = song["album"]["artists"][0]["name"]
            song_popularity = song["popularity"]
            song_image = get_image(song_image_url, song_location, song_name, 200, 200)

            song_information = [song_name, song_artist, song_popularity, song_audio, song_image, playlist_name]

            song_record_path = f"{record_path}/songs.csv"

            # Write song info to file
            write_to_csv_file(song_record_path, "a", song_information)

    return exist   