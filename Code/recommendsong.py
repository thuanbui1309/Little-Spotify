import pandas as pd
import scipy.sparse
from implicit.als import AlternatingLeastSquares

def load_users_songs():
    # Load data from csv file
    users_songs = pd.read_csv("../Record/users_songs.csv")

    # Now, I will convert the data frame into a csr matrix
    # However, there is a problem that user name and song name in my database is in string format
    # But, to convert into scipy csr matrix, it must be numerical value
    # To solve this, I will using factorize to encode all the string value

    # Factorize values
    user_name_codes, user_name_index = pd.factorize(users_songs["User name"])
    song_name_codes, song_name_index = pd.factorize(users_songs["Song name"])

    # Update into data frames
    users_songs["user_code"] = user_name_codes
    users_songs["song_code"] = song_name_codes

    # Set index for df
    users_songs.set_index(["user_code", "song_code"], inplace=True)

    # Initialize elements of the matrix
    # Row is for user name, column is for song, data is play count
    data = users_songs.play_count
    row = users_songs.index.get_level_values(0)
    column = users_songs.index.get_level_values(1)

    matrix = (data, (row, column))

    coo = scipy.sparse.coo_matrix(matrix)

    # Return matrix, index of song name and user name to get recommendation
    return coo.tocsr(), user_name_index, song_name_index

def recommend_song(current_user):

    # Load data
    users_songs, user_name_index, song_name_index = load_users_songs()

    # Training model
    model = AlternatingLeastSquares(factors=64, regularization=0.05, alpha=2.0)
    model.fit(users_songs)

    # Get recommendations in id
    user_id = user_name_index.get_loc(current_user)
    recommend_id, scores = model.recommend(user_id, users_songs[user_id], N=1)

    # Get song name from id
    recommended_song = song_name_index[recommend_id[0]]

    return recommended_song