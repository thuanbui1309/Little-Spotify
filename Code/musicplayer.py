import customtkinter as ctk
import pygame
import random
import time
import os
import re
import editplaylist
from editrecord import remove_user, update_users_songs_record
from getplaylist import get_playlist, get_a_single_song
from mutagen.mp3 import MP3, MutagenError
from readdata import read_playlists, read_users
from recommendsong import recommend_song
from PIL import Image
from thefuzz import fuzz

ctk.set_default_color_theme("../Data/Theme.json") # Config the default theme of customtkinter

# Playlist menu frame, containing all the playlist available
class PlaylistMenu(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(width = 278, 
                       height = 378, 
                       fg_color = "#121212",
                       scrollbar_button_color = "#121212",
                       scrollbar_button_hover_color = "#121212"
                       )
        self.columnconfigure(1, pad=10)
    
# Main menu frame, containing some program option
class MainMenu(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.configure(width=300, 
                       height = 150, 
                       fg_color = "#121212"
                       )

        self.users = self.master.users

        self.font ="Cabin"
        self.logo = ctk.CTkImage(light_image=Image.open("../Data/spotify.png"), size=(55, 55))

        self.create_widget()

    def create_widget(self):
        # Generate_button
        self.logo_display = ctk.CTkLabel(self,
                                         image=self.logo,
                                         text=""
                                         )

        # Generate button that randomize a song to play
        self.random_song_button = ctk.CTkButton(self, 
                                                text="Suprise Me?",
                                                width=134,
                                                fg_color="#4CAF50",
                                                corner_radius=50, 
                                                hover_color="#393939", 
                                                text_color="#000000", 
                                                font=(self.font,13), 
                                                anchor="center",
                                                command=lambda : self.random_song()
                                                )

        # Generate a button that recommend a song to play based on users data
        self.recommend_song_button = ctk.CTkButton(self, 
                                                   text="Your Picks",
                                                   width=134,
                                                   fg_color="#4CAF50",
                                                   corner_radius=50, 
                                                   hover_color="#393939", 
                                                   text_color="#000000", 
                                                   font=(self.font,13), 
                                                   anchor="center",
                                                   command=self.recommend_song
                                                   )

        # Search entry allow user enter a string to search for a song
        self.search_entry = ctk.CTkEntry(self,
                                         width=278,
                                         corner_radius=50,
                                         placeholder_text="Type the song title here..."
                                         )
        self.search_entry.bind("<Return>", self.search_song) # Active search when press Enter

        # place all widget in frame
        self.logo_display.place(relx=0.147, rely=0.065)
        self.random_song_button.place(relx=0.015, rely=0.5)
        self.recommend_song_button.place(relx=0.49, rely=0.5)
        self.search_entry.place(relx=0.015, rely=0.73)

        self.create_users_combobox()

    def create_users_combobox(self):
        # Generate users combobox
        self.users_display = ctk.CTkComboBox(self,
                                             values=self.users,
                                             corner_radius=30,
                                             command=self.change_current_user)
        self.users_display.bind("<Return>", self.add_new_user) # Active search when press Enter
        self.users_display.bind("<Button-3>", self.remove_user) # Active search when press Enter
        self.users_display.place(relx= 0.48, rely=0.16)

        self.master.current_user = self.users_display.get()

    def change_current_user(self, chosen_name):
        current_user = chosen_name
        self.master.current_user = current_user

    def add_new_user(self, x):
        new_user = self.users_display.get()
        if new_user == None:
            pass
        else:
            if new_user not in self.users:
                self.users.append(new_user)
                with open("../Record/users.txt", "a") as file:
                    file.write(f"{new_user}\n")
                self.users_display.destroy()
                self.create_users_combobox()
                self.users_display.set(new_user)
            else:
                self.users_display.set(self.users[0])
        self.focus_set()

    def remove_user(self, x):
        removed_user = self.users_display.get()
        if removed_user in self.users:
            self.users.remove(removed_user)
            remove_user(removed_user)
            self.users_display.destroy()
            self.create_users_combobox()

    # This function randomly play a song
    # Using random to generate index for playlist and song then play the chosen song
    def random_song(self):
        playlist_index = random.randint(0, len(self.master.playlists) - 1)
        song_length = len(self.master.playlists[playlist_index].songs)
        song_index = random.randint(0, song_length - 1)

        if self.master.current_playlist_index == playlist_index and self.master.current_song_index == song_index:
            self.random_song

        self.master.open_playlist(playlist_index)
        self.master.open_song(song_index)

    def recommend_song(self):
        song = recommend_song(self.master.current_user)
        print(song)

        for i in range(len(self.master.playlists)):
            for j in range(len(self.master.playlists[i].songs)):
                if self.master.playlists[i].songs[j].name == song:
                    self.master.current_playlist_index = i
                    self.master.current_song_index = j
                    break
        self.master.open_song(self.master.current_song_index)

    def search_song(self, event):
        song_search = self.search_entry.get()
        if song_search != None:
            playlist_choose_index = 0
            song_choose_index = 0
            similarity_ratio = 0

            for i in range(len(self.master.playlists)):
                for j in range(len(self.master.playlists[i].songs)):
                    simple_ratio = fuzz.ratio(song_search, self.master.playlists[i].songs[j].name)
                    partial_ratio = fuzz.partial_ratio(song_search, self.master.playlists[i].songs[j].name)
                    token_sort_ratio = fuzz.token_sort_ratio(song_search, self.master.playlists[i].songs[j].name)
                    token_set_ratio = fuzz.token_set_ratio(song_search, self.master.playlists[i].songs[j].name)

                    ratio = max([simple_ratio, partial_ratio, token_sort_ratio, token_set_ratio])
                    
                    if ratio > similarity_ratio:
                        similarity_ratio = ratio
                        playlist_choose_index = i
                        song_choose_index = j

            self.master.open_playlist(playlist_choose_index)
            self.master.open_song(song_choose_index)
        self.search_entry.delete(0, len(song_search))
        self.master.focus_set()

# Playlist show frame, displaying the chosen playlist
class PlaylistShow(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(width=500, 
                       height = 150, 
                       fg_color = "#4CAF50"
                       )

# Song menu frame, containing all the songs available in chosen playlist
class SongMenu(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(width=478, 
                       height = 378, 
                       fg_color = "#121212",
                       scrollbar_button_color = "#121212",
                       scrollbar_button_hover_color = "#121212"
                       )

# Control menu, containing buttons controlling the chosen song
class ControlMenu(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(width=815, 
                       height = 120, 
                       fg_color = "#000000"
                       )

# Edit Window, which appears when user want to edit a playlist
class EditWindow(ctk.CTkToplevel):
    def __init__(self, master, index):
        super().__init__()
        self.master = master
        self.index = index
        self.title(f"{self.master.playlists[self.index].name}")
        self.geometry("600x550+490+100")
        self.attributes('-topmost', True)
        self.configure(fg_color="#000000")
        self.song_lists = [] # Contain all the songs inside that playlist
        self.create_widget()

    # Generate all widgets
    def create_widget(self):
        # This frame contains all the songs in checkbox format
        song_lists = ctk.CTkScrollableFrame(self,
                                            width=400,
                                            height=370,
                                            fg_color="#121212",
                                            )

        # Create instruction for user
        instruction = ctk.CTkLabel(song_lists,
                                   text=f"There are {len(self.master.playlists[self.index].songs)} songs available to edit in playlist {self.master.playlists[self.index].name}",
                                   wraplength=256,
                                   justify="center"
                                   )
        instruction.pack(anchor="n", pady=5)

        # Create checkbox for each song in chosen playlist
        for i in range(len(self.master.playlists[self.index].songs)):
            checkbox = ctk.CTkCheckBox(song_lists, 
                                       text=self.master.playlists[self.index].songs[i].name,
                                       )
            self.song_lists.append(checkbox)
            checkbox.pack(anchor="nw",pady=2)

        # Create buttons for editing
        # Add song button allows user to add song to chosen playlist
        # Remove song button allows user to remove a song from chosen playlist
        # Remove playlist allows user to remove the whole playlist

        add_song_button = ctk.CTkButton(self,
                                        text="Add new song",
                                        width=150,
                                        fg_color="#4CAF50", 
                                        hover_color="#393939",
                                        corner_radius=50,
                                        text_color="#000000", 
                                        text_color_disabled="#000000", 
                                        font=(self.master.font,13), 
                                        anchor="center",
                                        command=self.add_song
                                        )

        remove_song_button = ctk.CTkButton(self,
                                           text="Remove song",
                                           width=150,
                                           fg_color="#4CAF50", 
                                           hover_color="#393939",
                                           corner_radius=50,
                                           text_color="#000000", 
                                           text_color_disabled="#000000", 
                                           font=(self.master.font,13), 
                                           anchor="center",
                                           command=self.remove_checked_songs
                                           )

        remove_playlist_button = ctk.CTkButton(self,
                                               text="Remove playlist",
                                               width=150,
                                               fg_color="#4CAF50", 
                                               hover_color="#393939",
                                               corner_radius=50, 
                                               text_color="#000000", 
                                               text_color_disabled="#000000", 
                                               font=(self.master.font,13), 
                                               anchor="center",
                                               command=self.remove_playlist
                                               )

        song_lists.place(relx=0.14, rely=0.05)
        add_song_button.place(relx=0.09, rely=0.8)
        remove_song_button.place(relx=0.37, rely=0.8)
        remove_playlist_button.place(relx=0.65, rely=0.8)

    # This function creata a new window, in that window user can add new songs to chosen playlist
    def add_song(self):
        self.destroy()
        add_song_window = AddSongOption(self, self.index)

    # This function remove all checked songs
    # I use get() to detect which songs being pressed
    # Then I clear all records and audio for chosen songs
    # In case nothing is checked, nothing happens
    # There is a special case, when the chosen song is in another playlist
    # In this case, only delete the record for current playlist, but not delete the song audio
    def remove_checked_songs(self):
        for i in range(len(self.song_lists)):
            if self.song_lists[i].get() == 1:
                unique = True
                for j in range(len(self.master.playlists)):
                    if j != self.index:
                        for song in self.master.playlists[j].songs:
                            if song.name == self.master.playlists[self.index].songs[i].name:
                                unique = False
                        
                editplaylist.remove_song(self.master.playlists[self.index].songs[i].name, self.master.playlists[self.index].name, unique)
        
        # After remove the song, reload current program to update the changes
        self.master.playlists = read_playlists()
        self.master.clear_frame(self.master.song_menu)
        self.master.display_playlist()
        self.master.open_playlist(self.index)

        self.destroy() 

    # This function remove the chosen playlist
    # It works exactly the same as remove song:
    # Remove all record and file 
    def remove_playlist(self):
        editplaylist.remove_playlist(self.master.playlists[self.index].name)

        # Also reload program after removing playlist
        self.master.clear_frame(self.master.playlist_menu)
        self.master.clear_frame(self.master.playlist_show)
        self.master.clear_frame(self.master.song_menu)
        self.master.clear_frame(self.master.control_menu)

        self.master.playlists = read_playlists()
        if len(self.master.playlists) != 0:
            self.master.display_playlist()
            if self.master.current_playlist_index == len(self.master.playlists):
                self.master.current_playlist_index = 0
            self.master.open_playlist(self.master.current_playlist_index)
            self.master.current_song_index = 0
            if self.master.song_status != None:
                self.master.open_song(self.master.current_song_index)

        self.destroy()

# This window pops up when user when to directly delete a song
# It will appears when user press right mouse in a song
class RemoveSong(ctk.CTkToplevel):
    def __init__(self, master, index):
        super().__init__()
        self.master = master
        self.index = index
        self.playlist_name = self.master.playlists[self.master.current_playlist_index].name
        self.song_name = self.master.playlists[self.master.current_playlist_index].songs[self.index].name

        self.title(f"{self.song_name}")
        self.geometry("300x120+700+340")
        self.attributes('-topmost', True)
        self.configure(fg_color="#000000")

        self.create_widget()
    
    # This window works in sequence
    # First, create instructions and button
    # Secondly, if user press button(meaning confirm), then delete the song
    def create_widget(self):
        instruction = ctk.CTkLabel(self,
                                   text=f"Do you want to delete song {self.song_name} from playlist {self.playlist_name}?",
                                   wraplength=190,
                                   justify="center"
                                   )
        instruction.place(relx=0.215, rely=0.1)

        confirm_button = ctk.CTkButton(self,
                                       text="Remove song",
                                       width=150,
                                       fg_color="#4CAF50", 
                                       hover_color="#393939",
                                       corner_radius=50, 
                                       text_color="#000000", 
                                       text_color_disabled="#000000", 
                                       font=(self.master.font,13), 
                                       anchor="center",
                                       command=self.remove_song
                                       )
        confirm_button.place(relx=0.25, rely=0.6)

    def remove_song(self):
        unique = True
        for i in range(len(self.master.playlists)):
            if i != self.master.current_playlist_index:
                for song in self.master.playlists[i].songs:
                    if song.name == self.song_name:
                        unique = False

        editplaylist.remove_song(self.song_name, self.playlist_name, unique)
        self.master.playlists = read_playlists()
        self.master.clear_frame(self.master.song_menu)
        self.master.open_playlist(self.master.current_playlist_index)
        if self.master.current_song_index == self.index:
            if self.master.current_song_index == len(self.master.playlists[self.master.current_playlist_index].songs):
                self.master.current_song_index = 0
            self.master.open_song(self.master.current_song_index)
        
        self.destroy()

# This window use to allow user to add new song to playlist
# It has 2 options, each one is represented by a button
# There is also an instruction above to help user
class AddSongOption(ctk.CTkToplevel):
    def __init__(self, master, index):
        super().__init__()
        self.master = master
        self.index = index

        self.title(f"Add song to playlist {self.master.master.playlists[self.index].name}")
        self.geometry("500x200+570+340")
        self.attributes('-topmost', True)
        self.configure(fg_color="#000000")

        self.create_widget()

    def create_widget(self):
        # Instructions
        instruction = ctk.CTkLabel(self,
                                   text=f"You have 2 options to add new songs:\n1. Using Spotify to add new song\n2. Add existing songs to this playlist",
                                   wraplength=256,
                                   justify="center",
                                   font=(self.master.master.font,16)
                                   )
        instruction.place(relx=0.25, rely=0.15)

        # Add song from Spotify
        new_song_button = ctk.CTkButton(self,
                                        text="Add new song from Spotify songs",
                                        width=150,
                                        fg_color="#4CAF50", 
                                        hover_color="#393939",
                                        corner_radius=50, 
                                        text_color="#000000", 
                                        text_color_disabled="#000000", 
                                        font=(self.master.master.font,13), 
                                        anchor="center",
                                        command=self.add_spotify_song
                                        )
        new_song_button.place(relx=0.05, rely=0.7)

        # Add song locally
        new_song_from_existing_button = ctk.CTkButton(self,
                                                      text="Add song from existing songs",
                                                      width=150,
                                                      fg_color="#4CAF50", 
                                                      hover_color="#393939",
                                                      corner_radius=50, 
                                                      text_color="#000000", 
                                                      text_color_disabled="#000000", 
                                                      font=(self.master.master.font,13), 
                                                      anchor="center",
                                                      command=self.add_existing_song
                                                      )
        new_song_from_existing_button.place(relx=0.55, rely=0.7)

    # This function use spotdl to download a song to chosen playlist
    def add_spotify_song(self):
        self.destroy()
        instruction = "Give me a Spotify song and enjoy your music\n\nRemember: It must be a Spotify song link, any other kinds of links are not acceptable!\n\nProgram will be stopped during downloading process!"
        dialog = ctk.CTkInputDialog(text=instruction, 
                                    title=f"Add Spotify song to playlist {self.master.master.playlists[self.index].name}",
                                    fg_color = "#000000",
                                    button_fg_color="#4CAF50",
                                    button_hover_color="#4CAF50",
                                    button_text_color="#000000"
                                    )
        dialog.geometry("400x270+630+300")
        spotify_song_link = dialog.get_input()
        if spotify_song_link != None:
            if re.search(r"https://open.spotify.com/track/([a-zA-Z0-9]+)", spotify_song_link):
                exist = get_a_single_song(spotify_song_link, self.master.master.playlists[self.index].name, self.master.master.playlists[self.index].songs)

                # Reload program
                if exist == False:
                    self.master.master.playlists = read_playlists()
                    if self.master.master.current_playlist_index != 0:
                        self.master.master.clear_frame(self.master.master.song_menu)
                        self.master.master.open_playlist(self.master.master.current_playlist_index)
                else:
                    self.destroy()
                    announcement = ctk.CTkToplevel()
                    announcement.geometry("200x75+775+400")
                    announcement.title("Song exists")
                    announcement.configure(fg_color="#000000")

                    inbox = ctk.CTkLabel(announcement,
                                         text="Song already in playlist, please enter other songs!",
                                         wraplength=150,
                                         justify="center",
                                         )

                    inbox.pack(pady=10)

            else:
                self.add_spotify_song()

    # This function add existing song to chosen playlist
    def add_existing_song(self):
        self.destroy()
        add_from_existing_song = AddExistingSong(self, self.index)

# This window pops up when user choose to add an existing song to chosen playlist
# The idea is: Generate a frame that has all songs in other playlists in forms of checkboxes
# When button is pressed, all checked songs will be added into chosen playlist
class AddExistingSong(ctk.CTkToplevel):
    def __init__(self, master, index):
        super().__init__()
        self.master = master
        self.index = index
        self.playlists = self.master.master.master.playlists

        self.title(f"Add existing songs to playlist {self.playlists[self.index].name}")
        self.geometry("600x550+490+100")
        self.attributes('-topmost', True)
        self.configure(fg_color="#000000")
        self.song_left = None
        self.song_lists = []

        self.create_widget()

    def create_widget(self):
        self.song_left = self.get_left_songs()

        song_lists = ctk.CTkScrollableFrame(self,
                                            width=400,
                                            height=370,
                                            fg_color="#121212",
                                            )
                                    
        instruction = ctk.CTkLabel(song_lists,
                                   text=f"There are {len(self.song_left)} songs available to add to playlist {self.playlists[self.index].name}",
                                   wraplength=256,
                                   justify="center"
                                   )
        instruction.pack(anchor="n", pady=5)

        for i in range(len(self.song_left)):
            checkbox = ctk.CTkCheckBox(song_lists, 
                                       text=self.song_left[i],
                                       )
            self.song_lists.append(checkbox)
            checkbox.pack(anchor="nw",pady=2)

        add_song_button = ctk.CTkButton(self,
                                        text="Add new song",
                                        width=150,
                                        fg_color="#4CAF50", 
                                        hover_color="#393939",
                                        corner_radius=50,
                                        text_color="#000000", 
                                        text_color_disabled="#000000", 
                                        anchor="center",
                                        command=lambda song_lists = self.song_lists : self.add_song(song_lists)
                                        )

        song_lists.place(relx=0.15, rely=0.05)
        add_song_button.place(relx=0.37, rely=0.8)

    def get_left_songs(self):
        songs_left = []
        for i in range(len(self.playlists)):
            if i != self.index:
                for j in range(len(self.playlists[i].songs)):
                    exist = False

                    # Get name of song
                    song_name = self.playlists[i].songs[j].name

                    # Check if song in playlist or not
                    for m in range(len(self.playlists[self.index].songs)):
                        if self.playlists[self.index].songs[m].name == song_name:
                            exist = True

                    # Add song to song_left to display if song is not added yet
                    if song_name not in songs_left and exist == False:
                        songs_left.append(song_name)

        return songs_left

    def add_song(self, song_lists):
        for i in range(len(song_lists)):
            if self.song_lists[i].get() == 1:
                editplaylist.add_song(self.song_left[i], self.playlists[self.index].name)
        
        self.master.master.master.playlists = read_playlists()
        if self.master.master.master.current_playlist_index != 0:
            self.master.master.master.clear_frame(self.master.master.master.song_menu)
            self.master.master.master.open_playlist(self.master.master.master.current_playlist_index)

        self.destroy()

# Main class, control all frame inside program
class MusicPlayer(ctk.CTk):
    def __init__(self):
        # Config main app
        super().__init__()
        self.title("Little Music Player")
        self.geometry("815x630+340+35")
        self.iconbitmap("../Data/spotify.ico")
        self.resizable(False, False)

        self.users = read_users()
        self.current_user = None

        # Set up playlists and song
        self.playlists = read_playlists()
        self.current_playlist_index = 0
        self.current_song_index = None

        # Set up audio playing
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.set_endevent(pygame.USEREVENT)
        self.song_length = None
        self.volume = 50
        self.song_status = None
        self.current_time_display = None
        self.song_progress = None
        self.volume_bar = None
        self.finished = None

        self.font = "Cabin"

        # Set up main menu
        self.main_menu = MainMenu(self)
        self.main_menu.place(x=5, y=5)

        # Set up playlist menu
        self.playlist_menu = PlaylistMenu(self)
        self.playlist_menu.place(x=5, y=160)

        # Set up playlist show
        self.playlist_show = PlaylistShow(self)
        self.playlist_show.grid_propagate(False)
        self.playlist_show.place(x=310, y=5)
    
        # Set up song menu
        self.song_menu = SongMenu(self) 
        self.song_menu.place(x=310, y=160)

        # Set up control menu
        self.control_menu = ControlMenu(self)
        self.playlist_show.grid_propagate(False)
        self.control_menu.place(x=0, y=555)

        self.display_playlist()

        self.mainloop()

    def display_playlist(self):
        # Generate new_playlist button
        new_playlist_button = ctk.CTkButton(self.playlist_menu,
                                            text="Add new playlist",
                                            width=270,
                                            fg_color="#4CAF50", 
                                            hover_color="#393939",
                                            corner_radius=50, 
                                            text_color="#000000", 
                                            text_color_disabled="#ffffff", 
                                            font=(self.font,15), 
                                            anchor="center",
                                            command=self.add_playlist
                                            )
        new_playlist_button.grid(row=0, column=0, pady=10, sticky="ns")

        # Generate playlist buttons
        for i in range(len(self.playlists)):
            playlist_image_url = self.playlists[i].image
            playlist_image = ctk.CTkImage(light_image=Image.open(playlist_image_url), size=(38,38))
            playlist_button = ctk.CTkButton(master=self.playlist_menu,
                                            image=playlist_image,
                                            compound="left",
                                            text=self.playlists[i].name,
                                            height=50, 
                                            anchor="w", 
                                            fg_color="#121212", 
                                            hover_color="#393939", 
                                            border_width=1,
                                            border_color="#393939", 
                                            text_color="#ffffff", 
                                            text_color_disabled="#ffffff", 
                                            font=(self.font,15), 
                                            command=lambda playlist_index=i: self.open_playlist(playlist_index)
                                            )
            # When user right mouse click, it will open edit window for this playlist
            playlist_button.bind("<Button-3>", lambda event, i=i: self.edit_playlist(event, i))

            playlist_button.grid(row= i + 1, pady=5, columnspan=2, sticky="nsew")

    # Open playlist being pressed
    def open_playlist(self, playlist_index):
        self.current_playlist_index = playlist_index # Update playlist index

        # Get playlist information
        playlist_name = self.playlists[self.current_playlist_index].name
        playlist_image_url = self.playlists[self.current_playlist_index].image
        playlist_song = self.playlists[self.current_playlist_index].songs
        playlist_popularity  = 0
        for song in playlist_song:
            playlist_popularity += float(song.popularity) / len(playlist_song)

        # Reload frame
        self.clear_frame(self.playlist_show)

        playlist_image = ctk.CTkImage(light_image=Image.open(playlist_image_url),
                                                size=(120, 120))
        playlist_image_display = ctk.CTkLabel(self.playlist_show, 
                                              image=playlist_image, 
                                              text=""
                                              )  
        playlist_image_display.place(relx=0.04, rely=0.093)

        playlist_name_display = ctk.CTkLabel(self.playlist_show, 
                                             text=playlist_name[:11],
                                             width=100,
                                             height=20,
                                             fg_color="#4CAF50",
                                             text_color="#000000",
                                             anchor="sw",
                                             justify="left",
                                             font=("Bungee",45),
                                             corner_radius=0.5
                                             )
        playlist_name_display.place(relx=0.3, rely=0.02)

        playlist_info_display = ctk.CTkLabel(self.playlist_show, 
                                             text=f"Total Tracks: {len(playlist_song)} | Popularity: {round(playlist_popularity)}",
                                             width=100,
                                             height=20,
                                             fg_color="#4CAF50",
                                             text_color="#000000",
                                             anchor="nw",
                                             font=(self.font,15),
                                             corner_radius=0.5
                                             )
        playlist_info_display.place(relx=0.305, rely=0.65)

        self.clear_frame(self.song_menu)
        
        # Create buttons
        for i in range(len(playlist_song)):
            text = f"{playlist_song[i].name[:50]}"
            image_url = playlist_song[i].image
            song_image_display = ctk.CTkImage(light_image=Image.open(image_url),
                                                size=(40, 40))
            song_button = ctk.CTkButton(master=self.song_menu,
                                        image=song_image_display, 
                                        text=text,
                                        width=475,
                                        height=50, 
                                        anchor="w",
                                        fg_color="#121212", 
                                        hover_color="#393939",                         
                                        border_width=1,
                                        border_color="#393939", 
                                        text_color="#ffffff", 
                                        text_color_disabled="#ffffff",                 
                                        font=(self.font,15), 
                                        command=lambda song_index=i: self.open_song(song_index))
            # Pops up song edit widow when right mouse clicked
            song_button.bind("<Button-3>", lambda event, i=i: self.remove_song(event, i))

            song_button.grid(row= i + 1, pady=5, columnspan=2, sticky="nsew")

    # Open song to play
    def open_song(self, song_index):
        self.finished = False
        self.bind("<Up>", self.up_volume)
        self.bind("<Down>", self.down_volume)
        self.bind("<Right>", self.next_song)
        self.bind("<Left>", self.back_song)
        self.current_song_index = song_index # Update song index

        # Get song information
        song_name = self.playlists[self.current_playlist_index].songs[self.current_song_index].name
        song_artist = self.playlists[self.current_playlist_index].songs[self.current_song_index].artist
        song_image_url = self.playlists[self.current_playlist_index].songs[self.current_song_index].image

        song = MP3(os.path.abspath(self.playlists[self.current_playlist_index].songs[self.current_song_index].audio))
        self.song_length = song.info.length

        # Reload frame
        self.clear_frame(self.control_menu)

        # Generate widgets and place them
        song_image = ctk.CTkImage(light_image=Image.open(song_image_url),
                                  size=(45, 45))
        song_image_display = ctk.CTkLabel(self.control_menu, 
                                          image=song_image, 
                                          text=""
                                          )

        name_bar = ctk.CTkLabel(self.control_menu, 
                                text=f"{song_name[:18]}",
                                width=120,
                                height=33,
                                fg_color="transparent",
                                font=(self.font,14),
                                anchor="w",
                                justify="left"
                                )

        artist_bar = ctk.CTkLabel(self.control_menu, 
                                  text=f"{song_artist}\n",
                                  width=130,
                                  height=30,
                                  fg_color="transparent",
                                  font=(self.font,10),
                                  anchor="w",
                                  justify="left"
                                  )

        restart_song_button = ctk.CTkButton(master=self.control_menu, 
                                            text="🔂",
                                            width=17,
                                            height=40, 
                                            fg_color="transparent",
                                            hover=False,
                                            font=(self.font,25),
                                            command=self.restart_song
                                            )

        back_song_button = ctk.CTkButton(master=self.control_menu, 
                                         text="⏪",
                                         width=20,
                                         height=45,
                                         fg_color="transparent",
                                         hover=False,
                                         font=(self.font,25),
                                         command= lambda : self.back_song(self.control_menu)
                                         )
        
        play_button = ctk.CTkButton(master=self.control_menu, 
                                    text="▶",
                                    width=20,
                                    height=45,
                                    fg_color="transparent",
                                    hover=False,
                                    font=(self.font,25),
                                    command=self.pause_song
                                    )

        next_song = ctk.CTkButton(master=self.control_menu, 
                                  text="⏩",
                                  width=20,
                                  height=45,
                                  fg_color="transparent",
                                  hover=False,
                                  font=(self.font,25),
                                  command=lambda: self.next_song(self.control_menu)
                                  )
 
        random_song = ctk.CTkButton(master=self.control_menu, 
                                    text="🔀",
                                    width=20,
                                    height=40,
                                    fg_color="transparent",
                                    hover=False,
                                    font=(self.font,25),
                                    command=self.random_song
                                    )

        self.song_progress = ctk.CTkSlider(self.control_menu, 
                                           from_=0, 
                                           to=int(self.song_length),
                                           width=330,
                                           button_color="#ffffff",
                                           progress_color="#4CAF50",
                                           button_hover_color="#ffffff",
                                           command=self.update_song_progress
                                           )
        self.song_progress.set(0)

        volume_emoji = ctk.CTkLabel(master=self.control_menu, 
                                    text="🔈",
                                    height=40,
                                    fg_color="transparent",
                                    font=(self.font,25),
                                    )

        self.volume_bar = ctk.CTkSlider(self.control_menu,
                                   width=100,
                                   from_=0, 
                                   to=100,
                                   button_color="#ffffff",
                                   button_hover_color="#ffffff",
                                   command=self.update_volume
                                   )
        self.volume_bar.set(self.volume)
        song_image_display.place(relx=0.02, rely=0.105)

        name_bar.place(relx=0.08, rely=0.085)
        artist_bar.place(relx=0.08, rely=0.28)

        restart_song_button.place(relx=0.34)
        back_song_button.place(relx=0.40)
        play_button.place(relx=0.47)        
        next_song.place(relx=0.54)
        random_song.place(relx=0.61)

        self.song_progress.place(relx=0.2975, rely=0.4)

        volume_emoji.place(relx=0.83, rely=0.11)

        self.volume_bar.place(relx=0.85, rely=0.23)
        self.song_status = True
        self.play_song(self.current_song_index)

    # This function play the chosen song
    # Song is loaded and played usign pygame
    def play_song(self, song_index):
        pygame.mixer.music.load(self.playlists[self.current_playlist_index].songs[song_index].audio)

        song_length_display = ctk.CTkLabel(self.control_menu, 
                                           text=f"{self.reform_time(self.song_length)}",
                                           width=20,
                                           height=33,
                                           fg_color="transparent",
                                           font=(self.font,12),
                                           anchor="w",
                                           justify="left"
                                           )

        self.current_time_display = ctk.CTkLabel(self.control_menu, 
                                                 text="00:00",
                                                 width=20,
                                                 height=33,
                                                 fg_color="transparent",
                                                 font=(self.font,12),
                                                 anchor="e",
                                                 justify="left"
                                                 )

        self.current_time_display.place(relx=0.259, rely=0.333)
        song_length_display.place(relx=0.7, rely=0.335)

        pygame.mixer.music.play()
        pygame.mixer.music.set_volume(self.volume)

        update_users_songs_record(self.current_user, self.playlists[self.current_playlist_index].songs[self.current_song_index].name)

        self.display_current_time()

    # Display song time
    def display_current_time(self):
        current_time = pygame.mixer.music.get_pos() / 1000 # Get current song position
        real_current_time = self.reform_time(current_time) # Reform song to display

        if self.song_status == True:
            # Detect when song ends
            if current_time == -0.001: # When song finishs, song position  in pygame is set to -0.001
                self.current_time_display.configure(text=f"{real_current_time}")
                self.finished = True # Set song to finish
            # If song doesn't end, update song slider and current time
            else:
                # Check whether song_progress is in right pos or not
                current_time += 1 # real song pos is faster than time displayed 1s

                if self.song_progress.get() == current_time:
                    self.song_progress.set(int(current_time))
                else:
                    converted_time = self.reform_time(int(self.song_progress.get()))
                    self.current_time_display.configure(text=f"{converted_time}")

                    real_time = int(self.song_progress.get()) + 1
                    self.song_progress.set(real_time)

        if self.finished != True:
            # Keep update song time
            self.current_time_display.after(1000, self.display_current_time)
        else:
            # Move to next song
            self.next_song(self.control_menu) 

    def update_song_progress(self, x):
        self.current_time_display.configure(text=self.reform_time(int(self.song_progress.get())))
        pygame.mixer.music.load(self.playlists[self.current_playlist_index].songs[self.current_song_index].audio)
        pygame.mixer.music.play(start=int(self.song_progress.get()))
        if self.song_status == False:
            pygame.mixer.music.unpause()
            self.song_status = True
        

    # Pause song when pause button is pressed
    def pause_song(self):
        if self.song_status == True:
            pygame.mixer.music.pause()
            self.song_status = False
        else:
            pygame.mixer.music.unpause()
            self.song_status = True

    # Go to next song when next song button is pressed
    def next_song(self, x):
        for widget in self.control_menu.winfo_children():
            widget.destroy()
        self.current_song_index += 1
        if self.current_song_index == len(self.playlists[self.current_playlist_index].songs):
            self.current_song_index = 0
        self.open_song(self.current_song_index)

    # Go back song when back song button is pressed
    def back_song(self, x):
        self.current_song_index -= 1
        if self.current_song_index == -1:
            self.current_song_index = len(self.playlists[self.current_playlist_index].songs) - 1
        self.open_song(self.current_song_index)

    # Randomize a song to play
    def random_song(self):
        self.current_song_index = random.randint(0, len(self.playlists[self.current_playlist_index].songs) - 1)
        self.open_song(self.current_song_index)

    # Make the song runs continously
    def restart_song(self):
        pygame.mixer.music.rewind()
        self.current_time_display.configure(text=self.reform_time(0))
        self.song_progress.set(0)

    # Reform time to display to user
    def reform_time(self, time_seconds):
        reformed_time = time.strftime("%M:%S", time.gmtime(time_seconds))
        return reformed_time
    
    # Update volume of song
    # Not reset when change song
    def update_volume(self, x):
        self.volume = x
        pygame.mixer.music.set_volume(self.volume / 100)

    def up_volume(self, x):
        new_volume = self.volume_bar.get() + 5
        if new_volume > 100:
            new_volume = 100
        self.volume_bar.set(new_volume)
        self.update_volume(self.volume_bar.get())

    def down_volume(self, x):
        new_volume = self.volume_bar.get() - 5
        if new_volume < 0:
            new_volume = 0
        self.volume_bar.set(new_volume)
        self.update_volume(self.volume_bar.get())

    # Add playlist use spotify  playlist link
    # Open an input window, allow users to enter a spotify link and then download the song
    # Reload if user enter wrong format link
    def add_playlist(self):
        instruction = "Give me a Spotify playlist and enjoy your music\n\nRemember: It must be a Spotify playlist link, any other kinds of links are not acceptable!\n\nProgram will be stopped during downloading process"
        dialog = ctk.CTkInputDialog(text=instruction, 
                                    title="Add new playlist",
                                    fg_color = "#000000",
                                    button_fg_color="#4CAF50",
                                    button_hover_color="#4CAF50",
                                    button_text_color="#000000"
                                    )
        dialog.geometry("400x270+630+300")
        spotify_playlist_link = dialog.get_input()
        if spotify_playlist_link != None:
            if re.search(r"https://open.spotify.com/playlist/([a-zA-Z0-9]+)", spotify_playlist_link):
                get_playlist(spotify_playlist_link)
                self.playlists = read_playlists()
                self.display_playlist()
            else:
                self.add_playlist()

    #  Run edit playlist window
    def edit_playlist(self, event, i):
        edit_window = EditWindow(self, i)

    # Run remove song window
    def remove_song(self, event, i):
        remove_song_window = RemoveSong(self, i)

    # Clear chosen frame for reloading program
    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()