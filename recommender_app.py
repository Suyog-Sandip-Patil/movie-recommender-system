import streamlit as st
import pickle
import pandas as pd
import requests
from streamlit.components.v1 import iframe

# Set page config
st.set_page_config(
    page_title="🎬 Movie Recommender", 
    page_icon="🎥", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling and animations
st.markdown("""
    <style>
    /* Background gradient */
    .stApp {
        background: linear-gradient(to right, #141E30, #243B55);
        color: white;
    }

    /* Custom font */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    html, body, [class*="st-"] {
        font-family: 'Poppins', sans-serif;
    }

    /* Recommend button styling */
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        font-size: 18px;
        border-radius: 10px;
        padding: 10px 20px;
        transition: all 0.3s ease-in-out;
        border: none;
    }
    .stButton>button:hover {
        background-color: #E63946;
        transform: scale(1.05);
        color: white;
    }

    /* Movie name styles */
    .movie-title {
        font-size: 16px;
        font-weight: bold;
        text-align: center;
        color: white;
        margin-top: 10px;
    }

    /* Image fade-in animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: scale(0.8); }
        to { opacity: 1; transform: scale(1); }
    }

    /* Movie poster animation */
    .poster-container img {
        border-radius: 15px;
        animation: fadeIn 1s ease-in-out;
        transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
        width: 100%;
        height: auto;
    }
    .poster-container img:hover {
        transform: scale(1.05);
        box-shadow: 0px 10px 20px rgba(255, 255, 255, 0.3);
    }
    
    /* Select box styling */
    div[data-baseweb="select"] > div {
        background-color: rgba(255,255,255,0.1);
        color: white;
        border-radius: 10px;
    }
    
    /* Center the title */
    .title-wrapper {
        text-align: center;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# Fetch movie poster
def fetch_poster(movie_id):
    try:
        response = requests.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US')
        data = response.json()
        poster_path = data.get('poster_path', '')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
        return None
    except Exception as e:
        st.error(f"Error fetching poster: {e}")
        return None

# Recommendation function
def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

        recommended_movies = []
        recommended_movies_posters = []
        for i in movies_list:
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movies.append(movies.iloc[i[0]].title)
            poster = fetch_poster(movie_id)
            recommended_movies_posters.append(poster if poster else 'https://via.placeholder.com/500x750?text=No+Poster')
        
        return recommended_movies, recommended_movies_posters
    except Exception as e:
        st.error(f"Error generating recommendations: {e}")
        return [], []

# Load movie data
@st.cache_resource
def load_data():
    try:
        movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
        movies = pd.DataFrame(movies_dict)
        similarity = pickle.load(open('similarity.pkl', 'rb'))
        return movies, similarity
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), []

movies, similarity = load_data()

# App title
st.markdown("""
    <div class="title-wrapper">
        <h1 style='color: #FFD700;'>🎬 Movie Recommender System</h1>
        <p>Get personalized movie recommendations based on your selection</p>
    </div>
""", unsafe_allow_html=True)

# Main content
if movies.empty or len(similarity) == 0:
    st.error("Failed to load movie data. Please check the data files.")
else:
    # Movie selection dropdown
    selected_movie_name = st.selectbox(
        '🎥 Select a movie to get recommendations:',
        movies['title'].values,
        index=0 if not movies.empty else None
    )

    # Recommend button
    if st.button('🔍 Recommend Movies', type="primary"):
        with st.spinner('Finding similar movies...'):
            names, posters = recommend(selected_movie_name)

            if names and posters:
                # Display recommendations in a row
                st.markdown("<h2 style='text-align: center; color: white;'>🔥 Top 5 Recommendations</h2>", unsafe_allow_html=True)
                
                cols = st.columns(5)  # 5 Columns for movie display
                for col, name, poster in zip(cols, names, posters):
                    with col:
                        st.markdown(f"""
                            <div class="poster-container">
                                <img src='{poster}' alt='{name}'>
                            </div>
                            <div style="height: 60px; display: flex; align-items: center; justify-content: center;">
                                <p class='movie-title'>{name}</p>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("Could not generate recommendations. Please try another movie.")

# Add a footer
st.markdown("""
    <div style="text-align: center; margin-top: 50px; color: #aaa;">
        <p>Movie Recommender System • Powered by TMDB API</p>
    </div>
""", unsafe_allow_html=True)