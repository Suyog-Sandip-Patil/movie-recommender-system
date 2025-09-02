🎬 Movie Recommendation System
A personalized movie recommendation system built with Python, Machine Learning, and the TMDB API. This project features dual UI support via Flask and Streamlit, providing a seamless and interactive user experience.

✨ Features
🎯 Content-Based Filtering: Uses cosine similarity to recommend top 5 similar movies

🌐 Dual UI Support:

Flask-based web app with responsive HTML/CSS templates

Streamlit app for a quick and interactive experience

🔍 Dynamic Movie Search: Search for movies by title or query

🎭 Genre Browsing: Explore movies by genre

🖼️ Poster Display: Fetches movie posters dynamically via the TMDB API

💾 Efficient Data Handling: Uses Pickle to store precomputed movie data and similarity matrices

⚡ Caching & Optimization: Implements LRU caching and efficient API calls for improved performance

🎨 Custom Styling: Enhanced UI with custom CSS, animations, and responsive design

✅ Error Handling: Robust error handling and logging for reliability

🛠️ Tech Stack
Python

Flask

Streamlit

HTML & CSS

Scikit-learn

Pandas

TMDB API

Pickle

NLTK (for text processing)

Requests (for API integration)

📦 Installation & Setup
1. Clone the Repository
bash
git clone <repository-url>
cd movie-recommendation-system
2. Install Dependencies
bash
pip install -r requirements.txt
3. Set Up TMDB API Key
Get your API key from TMDB

Replace the TMDB_API_KEY in app.py with your key

4. Run the Flask App
bash
python app.py
5. Run the Streamlit App
bash
streamlit run recommender_app.py
📁 Project Structure
text
📦 movie-recommendation-system
├── 🐍 app.py                 # Flask application
├── 🐍 recommender_app.py     # Streamlit application
├── 📊 movie-recommendation-system.ipynb  # Jupyter notebook for model training
├── 🎬 movie_dict.pkl         # Pickled movie data
├── 📐 similarity.pkl         # Precomputed similarity matrix
├── 📁 templates/             # Flask HTML templates
├── 📁 static/               # Static assets (CSS, images)
└── 📁 responses/            # Contact form responses
🎥 How It Works
Data Processing:

Movie data is processed and features like genres, keywords, cast, and crew are extracted

Text data is stemmed and vectorized using CountVectorizer

Similarity Calculation:

Cosine similarity is computed between movie vectors

Recommendation:

Based on user input, the system returns the top 5 most similar movies

UI Interaction:

Users can select a movie and get recommendations with posters

🚀 Usage
Select a movie from the dropdown

Click the "Recommend" button

View the top 5 recommended movies with posters

📞 Contact & Support
For questions or support, please use the contact form in the Flask app or reach out via the provided channels.

📜 License
This project is licensed under the MIT License.

🙌 Acknowledgments
TMDB for providing the movie data API

Scikit-learn for machine learning tools

Flask & Streamlit for UI frameworks

🎉 Enjoy exploring movies with this recommendation system!
