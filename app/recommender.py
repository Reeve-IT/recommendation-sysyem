from __future__ import annotations

import ast
import os
from dataclasses import dataclass
from difflib import get_close_matches
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

MOVIES_PATH = BASE_DIR / "data" / "tmdb_5000_movies.csv"
CREDITS_PATH = BASE_DIR / "data" / "tmdb_5000_credits.csv"
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "").strip()
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
TMDB_API_BASE = "https://api.themoviedb.org/3"


@dataclass(slots=True)
class Recommendation:
    movie_id: int
    title: str
    overview: str
    genres: list[str]


class MovieRecommender:
    def __init__(self) -> None:
        self._movies = self._load_and_prepare()
        self._vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
        self._matrix = self._vectorizer.fit_transform(self._movies["tags"])
        self._similarity = cosine_similarity(self._matrix)

    def _load_and_prepare(self) -> pd.DataFrame:
        movies = pd.read_csv(MOVIES_PATH)
        credits = pd.read_csv(CREDITS_PATH)

        merged = pd.merge(movies, credits, on="title")
        merged = merged[["id", "title", "overview", "genres", "keywords", "cast", "crew"]]
        merged = merged.rename(columns={"id": "movie_id"}).dropna().reset_index(drop=True)

        for column in ["genres", "keywords", "cast", "crew"]:
            merged[column] = merged[column].apply(ast.literal_eval)

        merged["genres"] = merged["genres"].apply(self._extract_names)
        merged["keywords"] = merged["keywords"].apply(self._extract_names)
        merged["cast"] = merged["cast"].apply(self._extract_top_cast)
        merged["crew"] = merged["crew"].apply(self._fetch_director)

        for column in ["genres", "keywords", "cast", "crew"]:
            merged[column] = merged[column].apply(self._remove_spaces)

        merged["overview_text"] = merged["overview"]
        merged["overview"] = merged["overview"].apply(lambda text: text.split())
        merged["tags"] = merged["overview"] + merged["genres"] + merged["keywords"] + merged["cast"] + merged["crew"]
        merged["tags"] = merged["tags"].apply(lambda tokens: " ".join(tokens).lower())

        return merged[["movie_id", "title", "overview_text", "genres", "tags"]]

    @staticmethod
    def _extract_names(items: list[dict[str, Any]]) -> list[str]:
        return [item["name"] for item in items]

    @staticmethod
    def _extract_top_cast(items: list[dict[str, Any]]) -> list[str]:
        return [item["name"] for item in items[:3]]

    @staticmethod
    def _fetch_director(items: list[dict[str, Any]]) -> list[str]:
        for item in items:
            if item.get("job") == "Director":
                return [item["name"]]
        return []

    @staticmethod
    def _remove_spaces(items: list[str]) -> list[str]:
        return [item.replace(" ", "") for item in items]

    def list_titles(self) -> list[str]:
        return self._movies["title"].tolist()

    def find_title(self, query: str) -> str | None:
        titles = self.list_titles()
        lower_map = {title.lower(): title for title in titles}
        query_lower = query.strip().lower()

        if query_lower in lower_map:
            return lower_map[query_lower]

        partial_matches = [title for title in titles if query_lower in title.lower()]
        if partial_matches:
            return partial_matches[0]

        close = get_close_matches(query, titles, n=1, cutoff=0.6)
        return close[0] if close else None

    def _build_tmdb_enrichment(self, movie_id: int) -> dict[str, Any]:
        if not TMDB_API_KEY:
            return {"poster_url": None, "trailer_url": None, "tmdb_id": movie_id}

        details_url = f"{TMDB_API_BASE}/movie/{movie_id}"
        videos_url = f"{TMDB_API_BASE}/movie/{movie_id}/videos"

        try:
            details_response = requests.get(
                details_url,
                params={"api_key": TMDB_API_KEY, "language": "en-US"},
                timeout=10,
            )
            details_response.raise_for_status()
            details = details_response.json()
        except requests.RequestException:
            return {"poster_url": None, "trailer_url": None, "tmdb_id": movie_id}

        poster_path = details.get("poster_path")
        poster_url = f"{TMDB_IMAGE_BASE}{poster_path}" if poster_path else None

        trailer_url = None
        try:
            videos_response = requests.get(
                videos_url,
                params={"api_key": TMDB_API_KEY, "language": "en-US"},
                timeout=10,
            )
            videos_response.raise_for_status()
            videos = videos_response.json().get("results", [])
            trailer = next(
                (
                    video
                    for video in videos
                    if video.get("site") == "YouTube" and video.get("type") == "Trailer" and video.get("key")
                ),
                None,
            )
            if trailer:
                trailer_url = f"https://www.youtube.com/watch?v={trailer['key']}"
        except requests.RequestException:
            trailer_url = None

        return {
            "poster_url": poster_url,
            "trailer_url": trailer_url,
            "tmdb_id": movie_id,
            "vote_average": details.get("vote_average"),
            "release_date": details.get("release_date"),
            "runtime": details.get("runtime"),
        }

    @lru_cache(maxsize=256)
    def _cached_tmdb_enrichment(self, movie_id: int) -> dict[str, Any]:
        return self._build_tmdb_enrichment(movie_id)

    def recommend(self, query: str, limit: int = 5) -> dict[str, Any]:
        matched_title = self.find_title(query)
        if matched_title is None:
            return {
                "query": query,
                "matched_title": None,
                "results": [],
                "message": "Movie not found. Try another title.",
            }

        movie_index = self._movies[self._movies["title"] == matched_title].index[0]
        distances = self._similarity[movie_index]
        scored = sorted(list(enumerate(distances)), key=lambda item: item[1], reverse=True)[1 : limit + 1]

        results: list[dict[str, Any]] = []
        for index, score in scored:
            row = self._movies.iloc[index]
            enrichment = self._cached_tmdb_enrichment(int(row["movie_id"]))
            results.append(
                {
                    "movie_id": int(row["movie_id"]),
                    "title": row["title"],
                    "overview": row["overview_text"],
                    "genres": row["genres"],
                    "similarity": round(float(score), 4),
                    **enrichment,
                }
            )

        return {
            "query": query,
            "matched_title": matched_title,
            "results": results,
            "message": None,
        }


recommender = MovieRecommender()
