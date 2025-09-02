from flask import Flask, render_template, request, jsonify
import requests
import random
import logging
import pickle
import pandas as pd
from functools import lru_cache
from flask import Flask, request, jsonify
import os
from datetime import datetime
app = Flask(__name__)

RESPONSES_DIR = 'responses'
os.makedirs(RESPONSES_DIR, exist_ok=True)

# Configuration
TMDB_API_KEY = '8265bd1679663a7ea12ac168da84d2e8'
TMDB_BASE_URL = 'https://api.themoviedb.org/3'
POSTER_BASE_URL = 'https://image.tmdb.org/t/p/w500/'
BACKDROP_BASE_URL = 'https://image.tmdb.org/t/p/original/'

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load recommendation data
try:
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    movies_df = pd.DataFrame(movies_dict)
    similarity_matrix = pickle.load(open('similarity.pkl', 'rb'))
    logger.info("Successfully loaded recommendation data")
    
    # Ensure we have the required columns
    if 'title' not in movies_df.columns or 'movie_id' not in movies_df.columns:
        logger.error("Movie data is missing required columns (title and/or movie_id)")
        movies_df = pd.DataFrame()
        similarity_matrix = []
except Exception as e:
    logger.error(f"Error loading recommendation data: {e}")
    movies_df = pd.DataFrame()
    similarity_matrix = []

# Cache frequently accessed data
@lru_cache(maxsize=32)
def get_cached_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching data from {url}: {e}")
        return None

def get_random_backdrop():
    """Fetch a random backdrop image from popular movies"""
    try:
        data = get_cached_data(f'{TMDB_BASE_URL}/movie/popular?api_key={TMDB_API_KEY}')
        if data and data.get('results'):
            movies_with_backdrops = [m for m in data['results'] if m.get('backdrop_path')]
            if movies_with_backdrops:
                movie = random.choice(movies_with_backdrops)
                return f"{BACKDROP_BASE_URL}{movie['backdrop_path']}"
        return None
    except Exception as e:
        logger.error(f"Error getting random backdrop: {e}")
        return None

def get_all_genres():
    """Fetch all movie genres from TMDB"""
    try:
        data = get_cached_data(f'{TMDB_BASE_URL}/genre/movie/list?api_key={TMDB_API_KEY}')
        return data.get('genres', []) if data else []
    except Exception as e:
        logger.error(f"Error getting genres: {e}")
        return []

def get_genre_id(genre_name):
    """Map genre name to TMDB genre ID"""
    genre_mapping = {
        'Action': 28, 'Adventure': 12, 'Animation': 16, 'Comedy': 35,
        'Crime': 80, 'Documentary': 99, 'Drama': 18, 'Family': 10751,
        'Fantasy': 14, 'History': 36, 'Horror': 27, 'Music': 10402,
        'Mystery': 9648, 'Romance': 10749, 'Sci-Fi': 878, 'Thriller': 53,
        'War': 10752, 'Western': 37
    }
    return genre_mapping.get(genre_name)

@lru_cache(maxsize=128)
def fetch_poster(movie_id):
    """Fetch movie poster with caching"""
    try:
        data = get_cached_data(f'{TMDB_BASE_URL}/movie/{movie_id}?api_key={TMDB_API_KEY}')
        if data and data.get('poster_path'):
            return f"{POSTER_BASE_URL}{data['poster_path']}"
        return None
    except Exception as e:
        logger.error(f"Error fetching poster for {movie_id}: {e}")
        return None

def get_recommendations(movie_title):
    """Generate movie recommendations based on similarity"""
    try:
        if movies_df.empty or movie_title not in movies_df['title'].values:
            return []
            
        movie_index = movies_df[movies_df['title'] == movie_title].index[0]
        distances = similarity_matrix[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        
        recommendations = []
        for i in movies_list:
            movie_id = movies_df.iloc[i[0]].movie_id
            recommendations.append({
                'id': movie_id,
                'title': movies_df.iloc[i[0]].title,
                'poster_path': fetch_poster(movie_id) or '/static/placeholder.jpg'
            })
        return recommendations
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return []

@app.route('/')
def index():
    """Main page with movie recommendations"""
    try:
        # Fetch trending and popular movies
        trending_data = get_cached_data(f'{TMDB_BASE_URL}/trending/movie/week?api_key={TMDB_API_KEY}')
        popular_data = get_cached_data(f'{TMDB_BASE_URL}/movie/popular?api_key={TMDB_API_KEY}')
        
        trending_movies = trending_data.get('results', [])[:10] if trending_data else []
        popular_movies = popular_data.get('results', [])[:10] if popular_data else []
        
        # Mock user preferences
        recommended_movies = []
        for genre in ['Action', 'Comedy']:  # Example preferences
            genre_id = get_genre_id(genre)
            if genre_id:
                genre_data = get_cached_data(
                    f'{TMDB_BASE_URL}/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}'
                )
                if genre_data:
                    recommended_movies.extend(genre_data.get('results', [])[:5])

        # Remove duplicates
        recommended_movies = list({m['id']: m for m in recommended_movies}.values())

        # Prepare all movies for dropdown
        all_movies = []
        if not movies_df.empty:
            all_movies = movies_df[['title', 'movie_id']].rename(
                columns={'movie_id': 'id'}
            ).to_dict('records')

        return render_template(
            'index.html',
            trending_movies=trending_movies,
            popular_movies=popular_movies,
            recommended_movies=recommended_movies,
            genres=get_all_genres(),
            backdrop_url=get_random_backdrop(),
            all_movies=all_movies
        )
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return render_template('error.html', message="Failed to load movie data")

@app.route('/recommend', methods=['POST'])
def recommend():
    """API endpoint for movie recommendations"""
    try:
        data = request.get_json()
        if not data or 'movie_title' not in data:
            return jsonify({'error': 'Movie title is required'}), 400
            
        recommendations = get_recommendations(data['movie_title'])
        return jsonify(recommendations)
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        return jsonify({'error': 'Failed to generate recommendations'}), 500

@app.route('/search')
def search():
    """Search for movies"""
    try:
        query = request.args.get('query')
        if not query:
            return render_template('error.html', message="Please enter a search query")

        search_data = get_cached_data(f'{TMDB_BASE_URL}/search/movie?api_key={TMDB_API_KEY}&query={query}')
        search_results = search_data.get('results', []) if search_data else []

        return render_template(
            'search_results.html',
            query=query,
            search_results=search_results,
            backdrop_url=get_random_backdrop()
        )
    except Exception as e:
        logger.error(f"Search error: {e}")
        return render_template('error.html', message="Search failed")

@app.route('/movie/<int:movie_id>')
def movie_details(movie_id):
    """Movie details page"""
    try:
        movie_data = get_cached_data(
            f'{TMDB_BASE_URL}/movie/{movie_id}?api_key={TMDB_API_KEY}&append_to_response=videos'
        )
        if not movie_data:
            return render_template('error.html', message="Movie not found")

        similar_data = get_cached_data(
            f'{TMDB_BASE_URL}/movie/{movie_id}/similar?api_key={TMDB_API_KEY}'
        )
        similar_movies = similar_data.get('results', [])[:5] if similar_data else []

        backdrop = (
            f"{BACKDROP_BASE_URL}{movie_data['backdrop_path']}" 
            if movie_data.get('backdrop_path') 
            else get_random_backdrop()
        )

        return render_template(
            'movie_details.html',
            movie=movie_data,
            similar_movies=similar_movies,
            backdrop_url=backdrop
        )
    except Exception as e:
        logger.error(f"Movie details error: {e}")
        return render_template('error.html', message="Failed to load movie details")

@app.route('/genre/<int:genre_id>')
def genre_movies(genre_id):
    """Movies by genre"""
    try:
        genre_data = get_cached_data(
            f'{TMDB_BASE_URL}/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}'
        )
        genre_movies = genre_data.get('results', []) if genre_data else []

        return render_template(
            'genre_movies.html',
            genre_movies=genre_movies,
            backdrop_url=get_random_backdrop()
        )
    except Exception as e:
        logger.error(f"Genre movies error: {e}")
        return render_template('error.html', message="Failed to load genre movies")

@app.route('/profile')
def profile():
    """User profile page"""
    try:
        # Mock user data - replace with actual user data from database
        user = {
            'name': 'John Doe',
            'watchlist': [],
            'watched': [],
            'preferences': ['Action', 'Comedy']
        }

        return render_template(
            'profile.html',
            user=user,
            backdrop_url=get_random_backdrop()
        )
    except Exception as e:
        logger.error(f"Profile error: {e}")
        return render_template('error.html', message="Failed to load profile")
    
@app.route('/streamlit_recommender')
def streamlit_recommender():
    # This assumes your Streamlit app is running on port 8501
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Movie Recommender</title>
        <style>
            iframe {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                border: none;
            }
        </style>
    </head>
    <body>
        <iframe src="http://localhost:8501" allowfullscreen></iframe>
    </body>
    </html>
    """

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy-policy.html')

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    try:
        data = request.json
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f"contact_response_{timestamp}.txt"
        filepath = os.path.join(RESPONSES_DIR, filename)
        
        with open(filepath, 'w') as f:
            f.write(f"Name: {data['name']}\n")
            f.write(f"Email: {data['email']}\n")
            f.write(f"Subject: {data['subject']}\n")
            f.write(f"Message: {data['message']}\n")
            f.write(f"Timestamp: {data['timestamp']}\n")
        
        return jsonify({'success': True, 'message': 'Your message has been sent successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to send message: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True)