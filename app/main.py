from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .recommender import recommender


BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Movie Recommendation Prototype")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=200)
    limit: int = Field(default=5, ge=1, le=10)


@app.get("/")
def home() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/titles")
def titles() -> dict[str, list[str]]:
    return {"titles": recommender.list_titles()}


@app.post("/api/recommendations")
def recommendations(payload: SearchRequest) -> dict:
    return recommender.recommend(payload.query, limit=payload.limit)
