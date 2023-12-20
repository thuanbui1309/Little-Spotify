import csv
import os
from dotenv import load_dotenv

def remove_user(user_name):
    load_dotenv()
    users_record = os.getenv("users_path", "")
    users_songs_path = os.getenv("users_songs_path", "")

    users = []
    with open(users_record, "r") as file:
        for line in file.readlines():
            if line.strip() != user_name:
                users.append(line.strip())

    with open(users_record, "w") as file:
        for i in range(len(users)):
            if i < len(users[i]) - 1:
                file.write(f"{users[i]}\n")

    file_data = []
    with open(users_songs_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)

        for row in reader:
            if row[0] != user_name:
                file_data.append(row)

    with open(users_songs_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        for row in file_data:
            writer.writerow(row)

def update_users_songs_record(user_name, song_name):
    # print(user_name)
    # print(song_name)
    load_dotenv()
    users_songs_path = os.getenv("users_songs_path", "")

    file_data = []

    # Check if user has listened to this song before
    exist = False # exist means if record for this user and song exist or not

    with open(users_songs_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)

        for read_row in reader:
            if read_row[0] == user_name and read_row[1] == song_name:
                exist = True
                new_play_count = int(read_row[2]) + 1
                read_row[2] = new_play_count

            file_data.append(read_row)

    if exist == False: # Meaning the song is not exist before
        with open(users_songs_path, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            new_record = [user_name, song_name, 1]
            writer.writerow(new_record)

    else:
        with open(users_songs_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            for row in file_data:
                writer.writerow(row)