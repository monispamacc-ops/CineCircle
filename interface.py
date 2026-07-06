import streamlit as st
import pandas as pd
from db_manager import add_user, add_movie_to_db, add_rating_to_db, get_all_users, get_watchlist

# Set up the web page styling
st.set_page_config(page_title="The Movie Hub", page_icon="🎬", layout="wide")

st.title("🎬 Shared Movie Watchlist & Ratings")
st.markdown("Welcome! Add movies to the list and share your ratings with your friends.")

#---

# Sidebar section for user onboarding
st.sidebar.header("👤 Friend Profiles")
new_user = st.sidebar.text_input("Register a new friend name:")
if st.sidebar.button("Add Profile"):
    if new_user.strip():
        add_user(new_user.strip())
        st.sidebar.success(f"Added profile for '{new_user}'!")
        st.rerun()

# Fetch live user data list from database for dropdown selections
users_list = get_all_users()
user_options = {u['username']: u['user_id'] for u in users_list}

if not user_options:
    st.warning("⚠️ Please register at least one profile in the sidebar to get started!")
else:
    # Top Action Fields
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("➕ Add a New Movie to Watchlist")
        current_user_name = st.selectbox("Who is adding this movie?", options=list(user_options.keys()), key="add_movie_user")
        movie_to_search = st.text_input("Type Movie Title (e.g., Interstellar, Shrek):")
        
        if st.button("Add to Shared List"):
            if movie_to_search.strip():
                with st.spinner("Searching the internet API..."):
                    user_id = user_options[current_user_name]
                    add_movie_to_db(movie_to_search.strip(), user_id)
                    st.success(f"Processing complete for '{movie_to_search}'!")
                    st.rerun()

    with col2:
        st.subheader("⭐ Submit a Rating / Review")
        rating_user_name = st.selectbox("Your Name:", options=list(user_options.keys()), key="rate_user")
        
        # Get actual live movies currently sitting inside the database to review
        current_watchlist = get_watchlist()
        if not current_watchlist:
            st.info("Add a movie to the watchlist first before reviewing!")
        else:
            movie_titles = [m['title'] for m in current_watchlist]
            selected_movie_title = st.selectbox("Select Movie to Review:", options=movie_titles)
            
            # Find the corresponding unique ID manually from the database records or use simplified fetch matches
            # For our pipeline, we can pull the clean data directly
            from db_manager import connect_to_db
            conn = connect_to_db()
            cursor = conn.cursor()
            cursor.execute("SELECT movie_id FROM movies WHERE title = %s", (selected_movie_title,))
            m_id = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            score = st.slider("Your Rating Score:", min_value=1, max_value=5, value=5)
            review_text = st.text_area("Write a short review line:")
            
            if st.button("Submit Review"):
                r_user_id = user_options[rating_user_name]
                add_rating_to_db(m_id, r_user_id, score, review_text)
                st.success("Review uploaded safely!")
                st.rerun()

    #---
    
    # Bottom Section: Displaying the Live Shared Dashboard Table
    st.subheader("📊 Community Watchlist Dashboard")
    watchlist_data = get_watchlist()
    
    if watchlist_data:
        # Convert our clean dictionary responses into a beautiful visual dashboard dataframe table
        df = pd.DataFrame(watchlist_data)
        df.columns = ["Movie Title", "Year", "Genre", "Added By", "Avg Rating (Stars)", "Total Reviews Saved"]
        st.dataframe(df, use_container_width=True)
    else:
        st.info("The watchlist dashboard is currently empty. Add your first movie title above!")