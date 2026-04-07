# Movie Recommendation Prototype

A simple FastAPI website that recommends movies based on a user search. The frontend is plain HTML, CSS, and vanilla JavaScript, and the backend uses TMDB movie metadata to return similar titles plus live poster and trailer links.

## What it does

- Loads the TMDB movies and credits CSV files from `data/`
- Builds a text-based similarity model from movie overview, genres, keywords, cast, and director
- Enriches each recommendation with TMDB poster and trailer data using the movie ID
- Accepts a movie title from the user
- Returns 5 similar movies in a browser UI

## Setup

1. Add your TMDB API key to `.env`:

   `TMDB_API_KEY=your_tmdb_api_key_here`

2. Install dependencies:

   `pip install -r requirements.txt`

3. Start the app:

   `uvicorn app.main:app --reload`

4. Open the site:

   `http://127.0.0.1:8000`
