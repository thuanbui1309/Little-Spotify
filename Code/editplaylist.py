import csv
import os
from dotenv import load_dotenv
from getplaylist import subprocess_command

def add_song(song_name, playlist):
    load_dotenv()
    data_path = os.getenv("data_path", "")
    record_path = os.getenv("record_path", "")

    # Add song information to song record
    file_data = []
    with open(f"{record_path}/songs.csv", "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            exist = False
            if row[0] == song_name:
                for file in file_data:
                    if file[0] == song_name:
                        exist = True

                if exist == False:
                    row[5] = playlist
                    file_data.append(row)

    with open(f"{record_path}/songs.csv", "a", encoding="utf-8", newline='') as write_file:
        writer = csv.writer(write_file)
        for row in file_data:
            writer.writerow(row)

def remove_song(song_to_removed, playlist, unique):
    load_dotenv()
    data_path = os.getenv("data_path", "")
    record_path = os.getenv("record_path", "")

    # Get all songs record
    file_data = []
    with open(f"{record_path}/songs.csv", "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            file_data.append(row)

    # Remove invalid record
    for row in file_data:
        if row[0] == song_to_removed and row[5] == playlist:
            file_data.remove(row)

    # Update song record
    with open(f"{record_path}/songs.csv", "w", encoding="utf-8", newline='') as write_file:
        writer = csv.writer(write_file)
        for row in file_data:
            writer.writerow(row)

    # Remove audio file if song is unique
    if unique == True:
        subprocess_command(f"{data_path}/{playlist}", f"rmdir /s /q \"{song_to_removed}\"")
    
def remove_playlist(playlist_name):
    load_dotenv()
    data_path = os.getenv("data_path", "")
    record_path = os.getenv("record_path", "")

    # Delete playlist record
    file_data = []
    with open(f"{record_path}/playlists.csv", "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            file_data.append(row)

    with open(f"{record_path}/playlists.csv", "w", encoding="utf-8", newline='') as write_file:
        writer = csv.writer(write_file)
        for row in file_data:
            if row[0] != playlist_name:
                writer.writerow(row)

    # Delete songs record
    file_data = []
    with open(f"{record_path}/songs.csv", "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            file_data.append(row)
    
    with open(f"{record_path}/songs.csv", "w", encoding="utf-8", newline='') as write_file:
        writer = csv.writer(write_file)
        for row in file_data:
            if row[5] != playlist_name:
                writer.writerow(row)

    # Remove playlist audio
    subprocess_command(f"{data_path}", f"rmdir /s /q \"{playlist_name}\"")