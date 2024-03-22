# Streamlit App with Movie Posters

import streamlit as st
import pickle
import requests
from recommendation_utils import get_similar_movies

# Function to get movie poster URL from TMDb API using movie ID
def get_movie_poster(movie_id):
    api_key = "c3f7575654e6dcad50266adcf6316cc9"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
        poster_path = response.json()["poster_path"]
        return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    else:
        return None

# Load the recommendation system from the pickled file
with open('recommendation_system.pkl', 'rb') as f:
    recommendation_system = pickle.load(f)

# Function to retrieve similar movies with posters
def get_similar_movies_with_posters(movie_title):
    similar_movies = get_similar_movies(movie_title, recommendation_system['cosine_sim'], recommendation_system['movie_list'])
    movie_posters = {}
    for movie in similar_movies:
        movie_id = recommendation_system['movie_id_mapping'].get(movie)
        if movie_id:
            poster_url = get_movie_poster(movie_id)
            if poster_url:
                movie_posters[movie] = poster_url
    return movie_posters

# Function to get tagline of selected movie
def get_movie_tagline(movie_title):
    movie_id = recommendation_system['movie_id_mapping'].get(movie_title)
    if movie_id:
        api_key = "c3f7575654e6dcad50266adcf6316cc9"
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
        response = requests.get(url)
        if response.status_code == 200:
            tagline = response.json()["tagline"]
            return tagline
    return None

# Set the title of the Streamlit app
st.title('Movie Recommendation System')

# Get the selected movie from the user
selected_movie = st.selectbox('Select a movie:', recommendation_system['movie_list'])

# Button to trigger the recommendations
if st.button('Get Recommendations'):
    # Check if a movie is selected
    if selected_movie:
        # Get tagline of selected movie
        tagline = get_movie_tagline(selected_movie)
        # Display tagline if available
        if tagline:
            st.write(tagline)
        
        # Get similar movies for the selected movie with posters
        similar_movies_with_posters = get_similar_movies_with_posters(selected_movie)
        # Display recommendations if available
        if similar_movies_with_posters:
            # Create columns for each recommendation
            cols = st.columns(len(similar_movies_with_posters))
            for movie, poster_url in similar_movies_with_posters.items():
                with cols.pop(0):
                    st.image(poster_url, caption=movie, use_column_width=True)
                    st.write(movie)
        # Display message if no recommendations found
        else:
            st.write('No recommendations found.')
    # Display message if no movie selected
    else:
        st.write('Please select a movie.')
