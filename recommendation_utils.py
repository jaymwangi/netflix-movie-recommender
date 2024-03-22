# recommendation_utils.py

# Import necessary libraries
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Define function to get similar movies
def get_similar_movies(movie_title, similarity_matrix, movie_list, top_n=5):
    """
    Function to get similar movies based on cosine similarity scores.

    Parameters:
        movie_title (str): The title of the movie for which recommendations are sought.
        similarity_matrix (numpy.ndarray): The cosine similarity matrix between movies.
        movie_list (list): List containing movie titles.
        top_n (int, optional): Number of similar movies to return. Defaults to 5.

    Returns:
        list: List of titles of similar movies.
    """
    # Check if movie_title exists in movie_list
    if movie_title in movie_list:
        # Get the index of the movie in the movie_list
        movie_index = movie_list.index(movie_title)

        # Get similarity scores for the given movie
        similarity_scores = list(enumerate(similarity_matrix[movie_index]))

        # Sort movies based on similarity scores
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

        # Exclude the given movie itself from the list
        similarity_scores = similarity_scores[1:]

        # Get top N similar movies
        similar_movies = []
        for i in range(top_n):
            movie_index = similarity_scores[i][0]
            similar_movies.append(movie_list[movie_index])

        return similar_movies
    else:
        return f"Movie '{movie_title}' not found in the dataset."
