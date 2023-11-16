import requests


TMDB_API = "681539f9587e812081f2a55d6313ad42"
TMDB_base_url = "https://api.themoviedb.org/3/search/movie"
params ={
    "api_key": TMDB_API,
    "query": "The hobbit"
}

response = requests.get(TMDB_base_url, params=params)
data = response.json()['results']

for movie in data:
    print(movie['original_title'])

