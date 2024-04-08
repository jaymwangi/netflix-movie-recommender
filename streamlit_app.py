# Streamlit App with Movie Posters

import streamlit as st
import pickle
import requests
import gdown
from recommendation_utils import get_similar_movies
import os
import concurrent.futures 

# Function to download cosine_sim.pkl from Google Drive if not already downloaded
def download_cosine_sim():
    if not os.path.exists('cosine_sim.pkl'):
        file_id = '1PLOGTGZuynJ0nb611SZoNa9g2sPYorfy'
        output_file = 'cosine_sim.pkl'
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, output_file, quiet=False)

# Download cosine_sim.pkl from Google Drive if not already downloaded
download_cosine_sim()

# Load the other pickled files from the local directory
with open('movie_list.pkl', 'rb') as f:
    movie_list = pickle.load(f)

with open('movie_id_mapping.pkl', 'rb') as f:
    movie_id_mapping = pickle.load(f)

# Load the cosine similarity matrix
with open('cosine_sim.pkl', 'rb') as f:
    cosine_sim = pickle.load(f)

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


# Function to retrieve similar movies with posters asynchronously
def get_similar_movies_with_posters_async(movie_title):
    # Get similar movies
    similar_movies = get_similar_movies(movie_title, cosine_sim, movie_list)
    
    # Process similar movies asynchronously
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(get_movie_poster, movie_id_mapping.get(movie)): movie for movie in similar_movies}
        movie_posters = {futures[future]: future.result() for future in concurrent.futures.as_completed(futures)}
    
    return movie_posters

# Function to get tagline and starring actors of selected movie
def get_movie_details(movie_title):
    movie_id = movie_id_mapping.get(movie_title)
    if movie_id:
        api_key = "c3f7575654e6dcad50266adcf6316cc9"
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
        response = requests.get(url)
        if response.status_code == 200:
            movie_details = response.json()
            tagline = movie_details.get("tagline", "")
            
            # Get starring actors separately from the 'credits' endpoint
            credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={api_key}&language=en-US"
            credits_response = requests.get(credits_url)
            if credits_response.status_code == 200:
                credits_data = credits_response.json()
                actors = [actor['name'] for actor in credits_data.get('cast', [])[:2]]  # Get the first two actors
                return tagline, actors
            
    return None, None





# Set the title of the Streamlit app
st.title('Movie Recommendation System')

# Get the selected movie from the user
selected_movie = st.selectbox('Select a movie:', movie_list)

# Button to trigger the recommendations
if st.button('Get Recommendations'):
    # Check if a movie is selected
    if selected_movie:
        # Get tagline and starring actors of selected movie
        tagline, actors = get_movie_details(selected_movie)
        # Display tagline and starring actors if available
        # Display tagline and starring actors if available
        if tagline:
            st.write(tagline, align='center')
        if actors:
            st.write(f"Starring: {', '.join(actors)}", align='center')

        
        # Get similar movies for the selected movie with posters
        similar_movies_with_posters = get_similar_movies_with_posters_async(selected_movie)
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
