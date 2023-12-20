
# Little Music Player

Welcome to Little Music Player, my custom project for unit COS10009 Introduction to Programming at Swinburne University of Technology. 

## Overview
This program is written in Python, using customtkinter, an updated-UI version of tkinter for GUI. This project takes inspiration from Spotify, with a couple of extensions and adjustments to suit unit requirements and personal preferences. There are also other libraries used for specific function, which will be introduced in Features section.
## Features
My music player covers enough functions of a online music player, with some adjustments to be suitable for a local program.
- Automatic experience: 
The program is local running, but all data(songs information, images, audios, record,...) is loaded automatically. Even extensions like edit playlist, song, or add new song are also optimized to minize tasks for users, making users experience the smoothest possible.
- Unlimited songs with Spotify
Unlike normal music player program, my program has the ability to retrieve songs and data directly from Spotify. That means, if users want to have new songs, all they need to do is pasting a Spotify link, and let the program does its work! There is no limitations, except for one thing: your internet connection, so make sure your connection is fast and stable to have better experience using this extension.
- Play music, but not only that
Of course, whatever kinds of extension it has, the most important function of a music player is being able to play music. In Little Music Program, users can play whatever song in a chosen playlist, with different options like move to next/last song, play song again, randomly play a song. All rellevant information are displayed nicely, easy to see, so users have no difficult using my program.
- Simple searching
During listening to music, users are likely to want to search for a song to play. Normal searching can handle this well, but in many cases, users might don't remember the name of the song, or maybe this name is too long,... These cases make normal searching ineffective, as it can only detect when both the search and song name are 100% the same. To avoid that, in my program, Fuzzy Searching-a very effective string match algorithms-is applied, which improves the performance of program search and users experience significantly.
- Recommend song to users
One of the most important advancements of modern music player with traditional player is the ability to suggest songs for users. These recommendation systems in big music player like Spotify, ZingMp3, Youtube,... are very complicated, but they all share a common feature: Analysing past listening of all users and recommend songs based on the similarities between users, or, in a profesional term, is Collaborative Filtering. My music player applies this concept in a very basic but precise level, using Matrix Factorization, to recommend song for different profiles based on their previous record. The decent feature of this algorithms is data will be enriched over time, making the recommend process more and more precise.


## Documentation
To implement everything from scratch to the final project, I have used a lists of libraries. All main libraries documentation are listed below:

[Customtkinter GUI library- improved version of tkinter](https://customtkinter.tomschimansky.com/documentation/)

[Pygame for song processing](https://www.pygame.org/docs/ref/music.html#pygame.mixer.music.set_pos)

[Spotipy - Python library to work with Spotify API](https://spotipy.readthedocs.io/en/2.22.1/)

[Spotdl - Python library to download song from terminal](https://spotdl.readthedocs.io/en/latest/)

[TheFuzz - String Matching algorithm](https://github.com/seatgeek/thefuzz)

[Implicit - library for performing Collaborate Fifltering in recommendation system](https://benfred.github.io/implicit/)






## Acknowledgements
During the process of making this program, I want to give credit to these below projects for incredibly helpfull instructions for advanced programming concepts.
 - [Building a music player with Python and TKINTER](https://www.youtube.com/playlist?list=PLXLYwvNGGPoUzjKiGvuXm8qeiOYMnFria)
 - [Buid a mini version recommendation system like Spotify](https://youtu.be/gaZKjAKfe0s?si=glwyM9hOJcvDt3gc)
 - [How to retrive data from Spotify](https://engineeringfordatascience.com/posts/export_spotify_playlist_to_csv_using_python/)

