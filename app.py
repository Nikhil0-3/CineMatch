import pickle
import streamlit as st
import requests
import pandas as pd
import math
import urllib.parse

# Page configuration
st.set_page_config(
    page_title="🎬 CineMatch - Movie Recommendation System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Session State Initialization ---
if 'view' not in st.session_state:
    st.session_state.view = 'home'
if 'selected_movie' not in st.session_state:
    st.session_state.selected_movie = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1
if 'previous_view' not in st.session_state:
    st.session_state.previous_view = 'home'
if 'previous_page' not in st.session_state:
    st.session_state.previous_page = 1
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []
if 'selected_for_rec' not in st.session_state:
    st.session_state.selected_for_rec = ""
if 'top_movies' not in st.session_state:
    st.session_state.top_movies = None
if 'filtered_movies' not in st.session_state:
    st.session_state.filtered_movies = None

# --- Enhanced CSS with Aurora Animation and Professional UI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

    /* --- Base & Background --- */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #000 !important;
        color: #ffffff;
        font-family: 'Poppins', sans-serif;
        min-height: 100vh;
    }
    
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0);
    }

    /* --- Aurora Background Animation --- */
    .aurora-container {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: -2;
        pointer-events: none;
        overflow: hidden;
    }
    .aurora {
        position: absolute;
        border-radius: 50%;
        mix-blend-mode: screen;
        animation: aurora-anim 12s infinite linear;
        opacity: 0.7;
    }
    @keyframes aurora-anim {
        0% { transform: translate(-50%, -50%) scale(1) rotate(0deg); opacity: 0.5; }
        50% { transform: translate(50%, 50%) scale(1.5) rotate(180deg); opacity: 0.3; }
        100% { transform: translate(-50%, -50%) scale(1) rotate(360deg); opacity: 0.5; }
    }
    .aurora-1 { 
        width: 80vmax; height: 80vmax; 
        top: 20%; left: 20%; 
        background: radial-gradient(circle, #00f2ea 0%, rgba(0, 242, 234, 0) 70%); 
        animation-duration: 15s; 
    }
    .aurora-2 { 
        width: 60vmax; height: 60vmax; 
        top: 60%; left: 60%; 
        background: radial-gradient(circle, #8f94fb 0%, rgba(143, 148, 251, 0) 70%); 
        animation-duration: 12s; 
        animation-direction: reverse; 
    }
    .aurora-3 { 
        width: 70vmax; height: 70vmax; 
        top: 30%; left: 80%; 
        background: radial-gradient(circle, #4e54c8 0%, rgba(78, 84, 200, 0) 70%); 
        animation-duration: 18s; 
    }

    .starfall-container {
        pointer-events: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 120px;
        z-index: -1;
    }
    .star {
        position: absolute;
        border-radius: 50%;
        opacity: 0.7;
        width: 8px;
        height: 8px;
        animation: fall 3s linear infinite;
    }
    .star.s1 { left: 5vw; animation-duration: 1.3s; background: #ffd700;}
    .star.s2 { left: 15vw; animation-duration: 2.0s; background: #4a90e2;}
    .star.s3 { left: 25vw; animation-duration: 2.7s; background: #ff69b4;}
    .star.s4 { left: 35vw; animation-duration: 2.2s; background: #43c6ac;}
    .star.s5 { left: 45vw; animation-duration: 2.8s; background: #fff;}
    .star.s6 { left: 55vw; animation-duration: 2.4s; background: #ffd700;}
    .star.s7 { left: 65vw; animation-duration: 2.0s; background: #4a90e2;}
    .star.s8 { left: 75vw; animation-duration: 1.9s; background: #ff69b4;}
    .star.s9 { left: 85vw; animation-duration: 2.2s; background: #43c6ac;}
    .star.s10 { left: 95vw; animation-duration: 1.8s; background: #fff;}
    @keyframes fall {
        0% { top: -20px; opacity: 0.8;}
        80% { opacity: 0.8;}
        100% { top: 110px; opacity: 0;}
    }
            
    /* --- Buttons & Interactive Elements --- */
    .stButton > button {
        border-radius: 8px; 
        border: 1px solid #00f2ea;
        background-color: transparent; 
        color: #00f2ea;
        transition: all 0.3s ease-in-out;
        padding: 0.5rem 1rem;
    }
    .stButton > button:hover {
        background-color: #00f2ea; 
        color: #1a1a2e;
        border-color: #00f2ea; 
        box-shadow: 0 0 15px #00f2ea;
    }
    .nav-btn {
        background: rgba(0,0,0,0.3); 
        backdrop-filter: blur(5px);
        color: white !important; 
        text-decoration: none; 
        border-radius: 10px;
        padding: 0.5rem 1.5rem; 
        font-weight: 600; 
        cursor: pointer;
        z-index: 1000; 
        border: 1px solid rgba(255,255,255,0.2);
        transition: all 0.2s ease-in-out;
        display: inline-block;
        margin-bottom: 1rem;
    }
    .nav-btn:hover {
        background: rgba(0, 242, 234, 0.8);
        box-shadow: 0 0 15px #00f2ea;
        color: #0f0c29 !important;
    }

    /* --- Movie Cards --- */
    .movie-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px; 
        padding: 1rem; 
        margin: 10px 0;
        transition: all 0.3s ease; 
        border: 1px solid transparent;
        min-height: 400px; 
        backdrop-filter: blur(5px);
    }
    .movie-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.4);
        border-color: #00f2ea;
    }
    .movie-poster {
        border-radius: 10px; 
        width: 100%; 
        height: 250px;
        object-fit: cover; 
        margin-bottom: 1rem;
    }
    .movie-title {
        font-weight: 600; 
        font-size: 1.1rem; 
        color: #ffffff;
        text-align: center; 
        height: 3.3em; 
        overflow: hidden;
    }

    /* --- Headers & Layout --- */
    .main-header {
        font-size: 3.5rem; 
        text-align: center;
        background: linear-gradient(45deg, #8f94fb, #00f2ea);
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent;
        padding-top: 2rem; 
        font-weight: 700;
        margin-bottom: 2rem;
        position: relative;
        z-index: 100;
    }
    .subtitle {
        text-align: center;
        color: #cccccc;
        margin-bottom: 3rem;
        font-size: 1.2rem;
    }
    .sidebar-header {
        font-size: 1.5rem; 
        font-weight: 700; 
        margin-bottom: 1.5rem; 
        text-align: center;
        padding: 10px; 
        background: rgba(0, 242, 234, 0.1); 
        border-radius: 10px;
    }

    /* --- Details Page --- */
    .details-container {
        position: relative;
        background: rgba(0,0,0,0.7); 
        backdrop-filter: blur(10px);
        padding: 2rem; 
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.2);
        overflow: hidden;
        z-index: 100;
    }
    .details-container::before {
        content: ''; 
        position: absolute; 
        top: 0; 
        left: 0; 
        right: 0; 
        bottom: 0;
        background-image: var(--bg-image);
        background-size: cover; 
        background-position: center;
        filter: blur(20px) brightness(0.4); 
        z-index: -1;
    }

    /* --- Footer --- */
    .footer {
        text-align:center; 
        padding:2rem; 
        margin-top:3rem; 
        color:#cccccc;
        border-top: 1px solid #4e54c8;
    }
    
    /* Fix for Streamlit elements */
    .stSelectbox, .stSlider, .stButton {
        position: relative;
        z-index: 100;
    }
</style>

<div class="aurora-container">
    <div class="aurora aurora-1"></div>
    <div class="aurora aurora-2"></div>
    <div class="aurora aurora-3"></div>
</div>
<div class="starfall-container">
    <div class="star s1"></div> <div class="star s2"></div>
    <div class="star s3"></div> <div class="star s4"></div>
    <div class="star s5"></div> <div class="star s6"></div>
    <div class="star s7"></div> <div class="star s8"></div>
    <div class="star s9"></div> <div class="star s10"></div>
</div>
""", unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_resource
def load_data():
    movies = pickle.load(open('movies_full.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    genres = pickle.load(open('genres.pkl', 'rb'))
    actors = pickle.load(open('actors.pkl', 'rb'))
    directors = pickle.load(open('directors.pkl', 'rb'))
    if 'year' not in movies.columns and 'release_date' in movies.columns:
        movies['year'] = pd.to_datetime(movies['release_date'], errors='coerce').dt.year
    return movies, similarity, genres, actors, directors

movies, similarity, genres, actors, directors = load_data()

# --- API & Helper Functions ---
@st.cache_data
def fetch_poster(movie_title):
    try:
        api_key = st.secrets["TMDB_API_KEY"]
        movie_id = movies[movies['title'] == movie_title]['movie_id'].values[0]
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
        data = requests.get(url).json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
    except Exception: 
        pass
    return "https://via.placeholder.com/500x750?text=Poster+Not+Available"

def fetch_movie_details(movie_title):
    try:
        movie_data = movies[movies['title'] == movie_title].iloc[0]
        return {
            'title': movie_data['title'],
            'overview': " ".join(movie_data.get('overview', [])) if isinstance(movie_data.get('overview'), list) else movie_data.get('overview', 'No overview available.'),
            'release_date': movie_data.get('release_date', 'N/A'),
            'runtime': movie_data.get('runtime', 'N/A'),
            'vote_average': movie_data.get('vote_average', 0),
            'genres': movie_data.get('genres_flat', []),
            'cast': movie_data.get('cast_flat', [])[:5],
            'directors': movie_data.get('director_flat', []),
            'poster': fetch_poster(movie_title)
        }
    except IndexError: 
        return None

def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        return [movies.iloc[i[0]].title for i in movies_list]
    except Exception: 
        return []

def filter_movies_from_state():
    df = movies.copy()
    genre = st.session_state.get('filter_genre', '-- Select Genre --')
    actor = st.session_state.get('filter_actor', '-- Select Actor --')
    director = st.session_state.get('filter_director', '-- Select Director --')
    years = st.session_state.get('filter_years')
    rating = st.session_state.get('filter_rating', 0.0)
    sort_by = st.session_state.get('filter_sort_by', 'popularity')

    if genre != "-- Select Genre --": 
        df = df[df['genres_flat'].apply(lambda x: genre in x if isinstance(x, list) else False)]
    if actor != "-- Select Actor --": 
        df = df[df['cast_flat'].apply(lambda x: actor in x if isinstance(x, list) else False)]
    if director != "-- Select Director --": 
        df = df[df['director_flat'].apply(lambda x: director in x if isinstance(x, list) else False)]
    if years and 'year' in df.columns: 
        df = df[(df['year'] >= years[0]) & (df['year'] <= years[1])]
    if rating > 0: 
        df = df[df['vote_average'] >= rating]
    if sort_by: 
        df = df.sort_values(by=sort_by, ascending=False)
    return df

@st.cache_data
def get_top_movies(n=50, sort_by='weighted_rating'):
    return movies.sort_values(by=sort_by, ascending=False).head(n)

# --- UI Display Functions ---
def display_movie_cards(movie_titles):
    cols = st.columns(5)
    for i, title in enumerate(movie_titles):
        with cols[i % 5]:
            encoded_title = urllib.parse.quote_plus(title)
            prev_view = st.session_state.get('view', 'home')
            prev_page = st.session_state.get('current_page', 1)

            # Use JavaScript to handle navigation to avoid page reload issues
            st.markdown(f"""
            <div onclick="window.location.href='?movie={encoded_title}&prev_view={prev_view}&prev_page={prev_page}'" 
                 style="cursor: pointer;">
                <div class="movie-card">
                    <img class="movie-poster" src="{fetch_poster(title)}" onerror="this.src='https://via.placeholder.com/500x750?text=Poster+Not+Available'">
                    <div class="movie-title">{title}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("<h2 class='sidebar-header'>🔎 Filter Movies</h2>", unsafe_allow_html=True)
    
    st.selectbox("Genre", ["-- Select Genre --"] + genres, key='filter_genre')
    st.selectbox("Actor", ["-- Select Actor --"] + actors, key='filter_actor')
    st.selectbox("Director", ["-- Select Director --"] + directors, key='filter_director')
    if 'year' in movies.columns:
        year_min, year_max = int(movies['year'].min()), int(movies['year'].max())
        st.slider("Year Range", year_min, year_max, (year_min, year_max), key='filter_years')
    else: 
        st.session_state.filter_years = None
    st.slider("Minimum Rating", 0.0, 10.0, 0.0, step=0.5, key='filter_rating')
    st.selectbox("Sort By", ["popularity", 'release_date', 'vote_average', 'weighted_rating'], key='filter_sort_by')

    if st.button("Apply Filters"):
        st.session_state.filtered_movies = filter_movies_from_state()
        st.session_state.view = 'filtered_results'
        st.session_state.current_page = 1
        st.rerun()

    st.markdown("<h2 class='sidebar-header'>🏆 Top Movies</h2>", unsafe_allow_html=True)
    st.write("")
    if st.button("Show Top Movies"):
        st.session_state.top_movies = get_top_movies()
        st.session_state.view = 'top_movies'
        st.session_state.current_page = 1
        st.rerun()

# --- Check URL Parameters ---
params = st.experimental_get_query_params()
if 'movie' in params:
    st.session_state.view = 'details'
    st.session_state.selected_movie = params['movie'][0]
    if 'prev_view' in params:
        st.session_state.previous_view = params['prev_view'][0]
    if 'prev_page' in params:
        st.session_state.previous_page = int(params['prev_page'][0])

# --- Main Page Content ---
st.markdown("<div style='position: relative; z-index: 1000;'>", unsafe_allow_html=True)
st.markdown("<a href='?view=home' target='_self' class='nav-btn'>🏠 Home</a>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>🎬 CineMatch</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Your Ultimate Movie Recommendation System</p>", unsafe_allow_html=True)

# --- Page Display Logic ---
if st.session_state.view == 'home':
    st.subheader("Get Instant Recommendations")
    selected_movie_name = st.selectbox("Select a movie you like:", movies['title'].values, key="main_selector")
    if st.button('Get Recommendations'):
        st.session_state.recommendations = recommend(selected_movie_name)
        st.session_state.selected_for_rec = selected_movie_name
        st.rerun()
    
    if st.session_state.recommendations:
        st.subheader(f"Because you liked '{st.session_state.selected_for_rec}':")
        display_movie_cards(st.session_state.recommendations)
    
    st.markdown("---")
    st.subheader("🔥 Top Picks For Today")
    top_picks = get_top_movies(n=5)
    display_movie_cards(top_picks['title'].tolist())

elif st.session_state.view == 'top_movies':
    st.header("Top Rated Movies")
    movie_df = st.session_state.get('top_movies', get_top_movies())
    if movie_df is not None and not movie_df.empty:
        MOVIES_PER_PAGE = 10
        total_pages = math.ceil(len(movie_df) / MOVIES_PER_PAGE)
        page = st.session_state.current_page
        start_idx = (page - 1) * MOVIES_PER_PAGE
        end_idx = start_idx + MOVIES_PER_PAGE
        paginated_titles = movie_df['title'].iloc[start_idx:end_idx].tolist()
        
        display_movie_cards(paginated_titles)
        st.write("")
        c1, c2, c3 = st.columns([3, 1, 3])
        if c1.button("⬅️ Previous", use_container_width=True, disabled=(page <= 1)):
            st.session_state.current_page = page - 1
            st.rerun()
        c2.markdown(f"<div style='text-align: center; margin-top: 0.5rem;'>Page {page} of {total_pages}</div>", unsafe_allow_html=True)
        if c3.button("Next ➡️", use_container_width=True, disabled=(page >= total_pages)):
            st.session_state.current_page = page + 1
            st.rerun()

elif st.session_state.view == 'filtered_results':
    st.header("Filtered Movie Results")
    
    filtered_df = st.session_state.get('filtered_movies')
    if filtered_df is None:
        filtered_df = filter_movies_from_state()
        st.session_state.filtered_movies = filtered_df
    
    if not filtered_df.empty:
        MOVIES_PER_PAGE = 10
        total_pages = math.ceil(len(filtered_df) / MOVIES_PER_PAGE)
        page = st.session_state.current_page
        start_idx = (page - 1) * MOVIES_PER_PAGE
        end_idx = start_idx + MOVIES_PER_PAGE
        paginated_titles = filtered_df['title'].iloc[start_idx:end_idx].tolist()
        
        display_movie_cards(paginated_titles)
        st.write("")
        c1, c2, c3 = st.columns([3, 1, 3])
        if c1.button("⬅️ Previous", use_container_width=True, disabled=(page <= 1)):
            st.session_state.current_page = page - 1
            st.rerun()
        c2.markdown(f"<div style='text-align: center; margin-top: 0.5rem;'>Page {page} of {total_pages}</div>", unsafe_allow_html=True)
        if c3.button("Next ➡️", use_container_width=True, disabled=(page >= total_pages)):
            st.session_state.current_page = page + 1
            st.rerun()
    else:
        st.warning("No movies found with the current filters. Please try different options.")

elif st.session_state.view == 'details':
    # Decode the movie title from the URL
    decoded_movie_title = urllib.parse.unquote_plus(st.session_state.selected_movie)
    details = fetch_movie_details(decoded_movie_title)
    
    if details:
        # Use a button with callback to navigate back
        if st.button("⬅️ Back to List"):
            st.session_state.view = st.session_state.previous_view
            st.session_state.current_page = st.session_state.previous_page
            st.rerun()

        st.markdown(f"<style> .details-container::before {{ --bg-image: url({details['poster']}); }} </style>", unsafe_allow_html=True)

        with st.container():
            st.markdown('<div class="details-container">', unsafe_allow_html=True)
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(details['poster'], use_column_width=True)
            with col2:
                st.title(details['title'])
                st.markdown(f"**Rating:** ⭐ {details['vote_average']:.1f}/10")
                st.markdown(f"**Runtime:** {details['runtime']} minutes" if details['runtime'] != 'N/A' else "")
                st.markdown(f"**Genres:** {', '.join(details['genres'])}")
                st.markdown(f"**Cast:** {', '.join(details['cast'])}")
                st.markdown(f"**Director(s):** {', '.join(details['directors'])}")
                st.subheader("Overview")
                st.write(details['overview'])
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error("Could not load movie details.")
        if st.button("⬅️ Back to Home"):
            st.session_state.view = 'home'
            st.rerun()

# --- Footer ---
st.markdown(
    """
    <div class="footer">
        <p>Nikhil More | nikhil030304@gmail.com</p>
        <p>CineMatch © 2025</p>
    </div>
    """, 
    unsafe_allow_html=True
)
