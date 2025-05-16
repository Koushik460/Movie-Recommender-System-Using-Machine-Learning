import pickle
import streamlit as st
import requests

API_KEY = "3e85d9045b7e2d260d7418f6d8724cfd"  # Use your valid TMDB API key

def fetch_poster(movie_id):
    """
    Fetch poster URL from TMDB API.
    Returns None if poster is missing or request fails.
    """
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raises HTTPError for bad status
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
    except requests.RequestException:
        pass
    return None

def recommend(movie):
    """
    Recommend up to 5 movies similar to input movie with valid posters.
    """
    try:
        index = movies[movies['title'] == movie].index[0]
    except IndexError:
        st.error("Movie not found in database.")
        return [], []

    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:]:
        movie_id = movies.iloc[i[0]].movie_id
        poster_url = fetch_poster(movie_id)

        if poster_url:
            recommended_movie_names.append(movies.iloc[i[0]].title)
            recommended_movie_posters.append(poster_url)

        if len(recommended_movie_names) == 5:
            break

    if len(recommended_movie_names) < 5:
        st.info(f"Only found {len(recommended_movie_names)} recommendations with posters.")

    return recommended_movie_names, recommended_movie_posters

# Streamlit UI
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.header('🎬 Movie Recommender System Using Machine Learning')

movies = pickle.load(open('artifacts/movie_list.pkl', 'rb'))
similarity = pickle.load(open('artifacts/similarity.pkl', 'rb'))

movie_list = movies['title'].values
selected_movie = st.selectbox("Type or select a movie from the dropdown", movie_list)

if st.button('Show Recommendation'):
    names, posters = recommend(selected_movie)

    if names:
        cols = st.columns(len(names))
        for i, col in enumerate(cols):
            with col:
                st.image(posters[i])
                st.caption(names[i])
    else:
        st.info("No recommendations available.")
