import requests

API_KEY = 'e6d1ae5' 

def fetch_movie_details(movie_title):
    # Formulate the URL request to OMDb API
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={API_KEY}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        # Check if the API actually found the movie
        if data.get("Response") == "True":
            movie_details = {
                "movie_id": data.get("imdbID"), # Use unique IMDb ID as our primary key
                "title": data.get("Title"),
                "release_year": int(data.get("Year")[:4]), # Grab first 4 digits of year
                "genre": data.get("Genre")
            }
            return movie_details
        else:
            print(f"Movie not found: {data.get('Error')}")
            return None
            
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Test the function!
if __name__ == "__main__":
    test_movie = "Interstellar"
    print(f"Searching for '{test_movie}'...")
    result = fetch_movie_details(test_movie)
    print(result)