import requests
import os
import time
import traceback

class TMDBAPI:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("TMDB_API_KEY")
        self.base_url = "https://api.themoviedb.org/3"
        self.poster_base = "https://image.tmdb.org/t/p/w500"

    def get_details(self, movie_id):
        if not self.api_key:
            return {"Error": "No TMDB API Key provided."}
        
        url = f"{self.base_url}/movie/{movie_id}"
        params = {"api_key": self.api_key}
        headers = {"User-Agent": "Cine-NLP/1.0", "Accept": "application/json"}
        
        for attempt in range(3):
            try:
                response = requests.get(url, params=params, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                if "id" not in data:
                    return {"Error": data.get("status_message", "Movie not found")}
                
                # Map TMDB fields to a consistent format
                formatted = {
                    "Title": data.get("title"),
                    "Year": data.get("release_date", "")[:4],
                    "Genre": ", ".join([g["name"] for g in data.get("genres", [])]),
                    "imdbRating": data.get("vote_average"),
                    "Plot": data.get("overview"),
                    "Poster": f"{self.poster_base}{data.get('poster_path')}" if data.get("poster_path") else "N/A",
                    "Language": data.get("original_language"),
                    "Type": "movie"
                }
                return formatted
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                print(f"Attempt {attempt+1} failed for details: {e}")
                if attempt == 2:
                    traceback.print_exc()
                    return {"Error": f"TMDB Details Fetch failed after 3 attempts: {str(e)}"}
                time.sleep(1)
            except Exception as e:
                traceback.print_exc()
                return {"Error": f"TMDB Unexpected Error: {str(e)}"}

    def search_movies(self, query, page=1):
        if not self.api_key:
            return {"Error": "No TMDB API Key provided."}
        
        url = f"{self.base_url}/search/movie"
        params = {"api_key": self.api_key, "query": query, "page": page}
        
        headers = {"User-Agent": "Cine-NLP/1.0", "Accept": "application/json"}
        
        for attempt in range(3):
            try:
                response = requests.get(url, params=params, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                # Map results
                results = []
                for m in data.get("results", []):
                    results.append({
                        "Title": m.get("title"),
                        "Year": m.get("release_date", "")[:4],
                        "imdbID": m.get("id"), # Use id as imdbID for consistency in UI logic
                        "Type": "movie",
                        "Poster": f"{self.poster_base}{m.get('poster_path')}" if m.get('poster_path') else "N/A"
                    })
                return {"Search": results}
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                print(f"Attempt {attempt+1} failed for search: {e}")
                if attempt == 2:
                    traceback.print_exc()
                    return {"Error": f"TMDB Search failed after 3 attempts: {str(e)}"}
                time.sleep(1)
            except Exception as e:
                traceback.print_exc()
                return {"Error": f"TMDB Search Unexpected Error: {str(e)}"}

    def is_configured(self):
        return self.api_key is not None
