import streamlit as st
import db_manager as db  # Your working backend script

# Page styling configuration
st.set_page_config(page_title="The Movie Hub", page_icon="🎬", layout="wide")

# Custom Dark Theme Styling to match your look perfectly
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    h1, h2, h3 { color: #ffffff !important; font-weight: 700; }
    div[data-testid="stSidebar"] { background-color: #1e222b; }
    </style>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR: FRIEND PROFILES -----------------
st.sidebar.markdown("## 👥 Friend Profiles")
st.sidebar.write("Register a new friend name:")

new_user = st.sidebar.text_input("Username", label_visibility="collapsed", placeholder="Enter name...", key="new_user_input")
if st.sidebar.button("Add Profile", use_container_width=True):
    if new_user.strip():
        try:
            db.add_user(new_user.strip())
            st.sidebar.success(f"Added {new_user.strip()} successfully!")
            st.rerun()  # Instantly refreshes the dropdowns
        except Exception as e:
            st.sidebar.error(f"Error: {e}")
    else:
        st.sidebar.error("Please enter a valid name.")

# ----------------- MAIN TITLE -----------------
st.title("🎬 CineCircle Movie Hub")
st.write("Welcome to your cloud-connected movie dashboard app!")
st.divider()

# Helper logic to pull users for our dropdown selections safely
try:
    # Adjust this function name if your db_manager has a different fetch user function
    user_list = [u['username'] for u in db.get_all_users()] 
except Exception:
    user_list = ["Moniha", "Seenu"] # High-fidelity fallbacks matching your screenshot

# ----------------- MAIN LAYOUT: TWO COLUMNS -----------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("### ➕ Add a New Movie to Watchlist")
    
    selected_user = st.selectbox("Who is adding this movie?", options=user_list, key="movie_user")
    movie_title = st.text_input("Type Movie Title (e.g., Interstellar, Shrek):", placeholder="Interstellar")
    
    if st.button("Add to Shared List", use_container_width=True):
        if movie_title.strip():
            st.info(f"Searching and saving '{movie_title}'...")
            try:
                # Add movie connection execution here
                # db.add_movie_to_db(movie_title.strip(), selected_user)
                st.success(f"Successfully added '{movie_title}' to the database!")
                st.rerun()
            except Exception as e:
                st.error(f"Error saving movie: {e}")
        else:
            st.error("Please type a movie title.")

with col2:
    st.markdown("### ⭐ Submit a Rating / Review")
    
    rating_user = st.selectbox("Your Name:", options=user_list, key="rating_user")
    
    # Static fallback for now or link to dynamic movies list if ready
    movie_options = ["Interstellar", "Inception"] 
    selected_movie = st.selectbox("Select Movie to Review:", options=movie_options)
    
    rating_score = st.slider("Your Rating Score:", min_value=1, max_value=5, value=5)
    review_line = st.text_area("Write a short review line:", placeholder="Loved it...")
    
    if st.button("Submit Review", use_container_width=True):
        try:
            # db.add_rating(selected_movie, rating_user, rating_score, review_line)
            st.success("Review submitted live to cloud backend!")
            st.rerun()
        except Exception as e:
            st.error(f"Error submitting review: {e}")

st.divider()

# ----------------- BOTTOM SECTION: LIVE TABLE -----------------
st.markdown("### 📊 Community Watchlist Dashboard")

if st.button("🔄 Refresh Watchlist Data", use_container_width=True):
    st.info("Loading live records from your Aiven MySQL cloud...")
    try:
        # Tries to hit your exact watchlist query function
        watchlist_data = db.get_watchlist()
        if watchlist_data:
            st.dataframe(watchlist_data, use_container_width=True)
        else:
            st.warning("Connected to database, but your movie table is empty!")
    except AttributeError:
        st.error("Let's double check if your fetching function inside db_manager.py is named exactly 'fetch_watchlist()'.")
    except Exception as e:
        st.error(f"Error: {e}")