import mysql.connector
from mysql.connector import Error
from movie_api import fetch_movie_details

def connect_to_db():
    """Establishes and returns a connection to the local MySQL database."""
    try:
        connection = mysql.connector.connect(
            host='mysql-7456575-cinecircle-hub-99.g.aivencloud.com',
            port=25858,
            user='avnadmin',
            password='AVNS_5liDS45j9oGDHGVzTca',
            database='defaultdb',
            ssl_disabled=False
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f" Error while connecting to MySQL: {e}")
        return None

def create_tables():
    """Creates the necessary tables in the cloud database using the exact yesterday schema."""
    conn = connect_to_db()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        
        # Drop old temporary tables to apply the clean yesterday schema
        #cursor.execute("DROP TABLE IF EXISTS ratings;")
        #cursor.execute("DROP TABLE IF EXISTS movies;")
        #cursor.execute("DROP TABLE IF EXISTS users;")
        
        # 1. Users Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE
        );
        """)
        
        # 2. Movies Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            movie_id VARCHAR(50) PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            release_year INT,
            genre VARCHAR(100),
            added_by_user_id INT,
            FOREIGN KEY (added_by_user_id) REFERENCES users(user_id) ON DELETE SET NULL
        );
        """)
        
        # 3. Ratings Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            rating_id INT AUTO_INCREMENT PRIMARY KEY,
            movie_id VARCHAR(50),
            user_id INT,
            score INT CHECK (score BETWEEN 1 AND 5),
            review_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            UNIQUE(movie_id, user_id)
        );
        """)
        
        conn.commit()
        print("Database schema successfully verified in the cloud!")
    except Error as e:
        print(f"Error creating tables: {e}")
    finally:
        cursor.close()
        conn.close()

def test_connection():
    """Quick helper function to verify our connection works."""
    print("Testing connection to 'movie_hub' database...")
    conn = connect_to_db()
    if conn:
        print("Connection successful! Python can talk to your MySQL server.")
        conn.close()
    else:
        print("X Connection failed. Check your password or ensure MySQL Server is running.")

# This ensures the test only runs if you execute this file directly
if __name__ == "__main__":
    test_connection()
    create_tables()  

def add_user(username):
    """Inserts a new friend into the users table."""
    conn = connect_to_db()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        query = "INSERT INTO users (username) VALUES (%s)"
        cursor.execute(query, (username,))
        conn.commit()
        print(f" Friend '{username}' added successfully!")
    except Error as e:
        # If the friend is already in the database, MySQL will gracefully let us know
        print(f"Note regarding user '{username}': {e}")
    finally:
        cursor.close()
        conn.close()


def add_movie_to_db(movie_title, user_id):
    """Fetches a movie from the API and saves it into the MySQL database."""
    # 1. Fetch live data from your working API script
    movie_data = fetch_movie_details(movie_title)
    if not movie_data:
        print(" Could not add movie because it wasn't found online.")
        return

    conn = connect_to_db()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        
        # 2. SQL query with ON DUPLICATE KEY UPDATE to prevent errors if a movie is added twice
        query = """
        INSERT INTO movies (movie_id, title, release_year, genre, added_by_user_id)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE title=title; 
        """
        
        values = (
            movie_data['movie_id'],
            movie_data['title'],
            movie_data['release_year'],
            movie_data['genre'],
            user_id
        )
        
        cursor.execute(query, values)
        conn.commit()
        print(f"{movie_data['title']}' ({movie_data['release_year']}) successfully saved to your database!")
        
    except Error as e:
        print(f"Database error: {e}")
    finally:
        cursor.close()
        conn.close()


def add_rating_to_db(movie_id, user_id, score, review_text):
    """Inserts or updates a user's movie rating and review."""
    conn = connect_to_db()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        # If a friend reviews the same movie again, this updates their score/text instead of crashing!
        query = """
        INSERT INTO ratings (movie_id, user_id, score, review_text)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE score=%s, review_text=%s;
        """
        values = (movie_id, user_id, score, review_text, score, review_text)
        cursor.execute(query, values)
        conn.commit()
        print(f" Rating of {score}/5 stars recorded successfully!")
    except Error as e:
        print(f" Database error while adding rating: {e}")
    finally:
        cursor.close()
        conn.close()

def add_rating_to_db_by_title(movie_title, user_id, score, review_text):
    conn = connect_to_db()
    if not conn: return
    try:
        cursor = conn.cursor()
        # Look up the ID based on the title
        cursor.execute("SELECT movie_id FROM movies WHERE title = %s", (movie_title,))
        result = cursor.fetchone()
        
        if result:
            movie_id = result[0]
            # Use your existing logic to insert
            query = """
            INSERT INTO ratings (movie_id, user_id, score, review_text)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE score=%s, review_text=%s;
            """
            values = (movie_id, user_id, score, review_text, score, review_text)
            cursor.execute(query, values)
            conn.commit()
        else:
            print("Movie not found!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

def delete_review_by_title(movie_title, user_id):
    conn = connect_to_db()
    if not conn: return
    try:
        cursor = conn.cursor()
        # Find the movie_id first, then delete
        cursor.execute("SELECT movie_id FROM movies WHERE title = %s", (movie_title,))
        result = cursor.fetchone()
        if result:
            movie_id = result[0]
            cursor.execute("DELETE FROM ratings WHERE movie_id = %s AND user_id = %s", (movie_id, user_id))
            conn.commit()
    except Exception as e:
        print(f"Error deleting review: {e}")
    finally:
        cursor.close()
        conn.close()

def delete_movie_and_all_ratings(movie_title):
    """Deletes all ratings for a movie, then the movie entry itself."""
    conn = connect_to_db()
    if not conn: return
    try:
        cursor = conn.cursor()
        
        # 1. Get the movie_id first to ensure it exists
        cursor.execute("SELECT movie_id FROM movies WHERE title = %s", (movie_title,))
        result = cursor.fetchone()
        
        if result:
            movie_id = result[0]
            
            # 2. Delete all ratings linked to this movie_id
            cursor.execute("DELETE FROM ratings WHERE movie_id = %s", (movie_id,))
            
            # 3. Now delete the movie record
            cursor.execute("DELETE FROM movies WHERE movie_id = %s", (movie_id,))
            
            conn.commit()
            print(f"Successfully deleted '{movie_title}' and its ratings.")
        else:
            print("Movie not found.")
            
    except Exception as e:
        print(f"Error deleting movie: {e}")
    finally:
        cursor.close()
        conn.close()

def get_all_users():
    """Fetches all registered users for the UI dropdown menu."""
    conn = connect_to_db()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True) # Returns results as handy Python dictionaries
        cursor.execute("SELECT user_id, username FROM users")
        return cursor.fetchall()
    except Error as e:
        print(f"❌ Error fetching users: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_watchlist():
    """Fetches the complete watchlist with titles, genres, who added them, and average ratings."""
    conn = connect_to_db()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        # An elegant SQL JOIN to pull together movies, creators, and their average scores
        query = """
        SELECT m.movie_id AS movie_id, m.title, m.release_year, m.genre, u.username AS added_by, 
               ROUND(AVG(r.score), 1) AS avg_rating, COUNT(r.rating_id) AS total_reviews
        FROM movies m
        LEFT JOIN users u ON m.added_by_user_id = u.user_id
        LEFT JOIN ratings r ON m.movie_id = r.movie_id
        GROUP BY m.movie_id, m.title, m.release_year, m.genre, u.username;
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Error as e:
        print(f" Error fetching watchlist: {e}")
        return []
    finally:
        cursor.close()
        conn.close()
# This block lets us test the code immediately by running this file directly
if __name__ == "__main__":
    print("--- Running Core Pipeline Test ---")
    
    # 1. Ensure Moniha exists and Inception is in the DB
    add_user("Moniha") 
    add_movie_to_db("Inception", user_id=1)
    
    # NEW TEST: Let's leave a 5-star review for Inception (IMDb ID: tt1375666)
    print("\n--- Testing Rating Insertion ---")
    add_rating_to_db(movie_id="tt1375666", user_id=1, score=5, review_text="Mind-blowing masterpiece!")
    
    # NEW TEST: Let's see if our global watchlist data reads back properly
    print("\n--- Current Watchlist Data ---")
    print(get_watchlist())
