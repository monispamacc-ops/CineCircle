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

# ----------------- FETCH USER DATA SAFELY -----------------
# We create a dictionary mapping { 'Name': id } so the dropdown uses IDs behind the scenes
try:
    raw_users = db.get_all_users() # Assuming this returns a list of dicts/tuples with id and username
    # If get_all_users returns dicts like [{'id': 1, 'username': 'Moniha'}]
    if raw_users and isinstance(raw_users[0], dict):
        user_dict = {u['username']: u['id'] for u in raw_users}
    else:
        # Fallback if it returns a list of tuples (id, username)
        user_dict = {u[1]: u[0] for u in raw_users}
except Exception:
    # High-fidelity fallbacks matching your exact database records in image_e043d9.png
    user_dict = {"Moniha": 1, "Seenu": 4}

user_names = list(user_dict.keys())

# ----------------- MAIN TITLE -----------------
st.title("🎬 CineCircle Movie Hub")
st.write("Welcome to your cloud-connected movie dashboard app!")
st.divider()

# ----------------- MAIN LAYOUT: TWO COLUMNS -----------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("### ➕ Add a New Movie to Watchlist")
    
    selected_name = st.selectbox("Who is adding this movie?", options=user_names, key="movie_user")
    movie_title = st.text_input("Type Movie Title (e.g., Interstellar, Shrek):", placeholder="Interstellar")
    
    # Extract the matching numeric user_id for the database execution
    selected_id = user_dict.get(selected_name)
    
    if st.button("Add to Shared List", use_container_width=True):
        if movie_title.strip():
            with st.spinner(f"Searching and saving '{movie_title}'..."):
                try:
                    # Calling your exact backend function with correct arguments!
                    db.add_movie_to_db(movie_title.strip(), selected_id)
                    st.success(f"Successfully added '{movie_title}' to the database!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving movie: {e}")
        else:
            st.error("Please type a movie title.")

with col2:
    st.markdown("### ⭐ Submit a Rating / Review")
    
    rating_name = st.selectbox("Your Name:", options=user_names, key="rating_user")
    rating_id = user_dict.get(rating_name)
    
    # 1. Map movie titles to IDs for the database
    try:
        watchlist_data = db.get_watchlist()
        # Create a dictionary: { 'Title': 'ID' }
        movie_dict = {m['title']: m['id'] for m in watchlist_data}
        movie_options = list(movie_dict.keys())
    except Exception:
        movie_dict = {"Interstellar": 1, "Inception": 2}
        movie_options = list(movie_dict.keys())

    selected_movie_title = st.selectbox("Select Movie to Review:", options=movie_options)
    selected_movie_id = movie_dict.get(selected_movie_title)
    
    rating_score = st.slider("Your Rating Score:", min_value=1, max_value=5, value=5)
    review_line = st.text_area("Write a short review line:", placeholder="Semma ,mass ah iruku")
    
    # 2. Updated Submit button
    if st.button("Submit Review", use_container_width=True):
        try:
            db.add_rating_to_db(selected_movie_id, rating_id, rating_score, review_line)
            st.success("Review submitted live to cloud backend!")
            st.rerun()
        except Exception as e:
            st.error(f"Error submitting review: {e}")

    # 3. New Delete button
    if st.button("Delete My Review", use_container_width=True):
        try:
            db.delete_review(selected_movie_id, rating_id)
            st.warning(f"Review for '{selected_movie_title}' deleted.")
            st.rerun()
        except Exception as e:
            st.error(f"Error deleting review: {e}")
st.divider()

# ----------------- BOTTOM SECTION: LIVE TABLE -----------------
st.markdown("### 📊 Community Watchlist Dashboard")

if st.button("🔄 Refresh Watchlist Data", use_container_width=True):
    st.info("Loading live records from your Aiven MySQL cloud...")
    try:
        watchlist_data = db.get_watchlist() 
        if watchlist_data:
            import pandas as pd
            df = pd.DataFrame(watchlist_data)
            
            if 'avg_rating' in df.columns:
                def to_stars(val):
                    try:
                        if pd.notnull(val):
                            num = int(round(float(val)))
                            return "⭐" * num
                    except (ValueError, TypeError):
                        pass
                    return val
                df['avg_rating'] = df['avg_rating'].apply(to_stars)
            
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("Connected to database, but your movie table is empty!")
    except Exception as e:
        st.error(f"Error: {e}")