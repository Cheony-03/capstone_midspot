from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import rooms_db

router = APIRouter(prefix="/api/rooms/{room_id}", tags=["Votes"])

category_votes: dict[str, dict[str, str]] = {}
place_votes: dict[str, dict[str, dict]] = {}

ALLOWED = {"cafe", "restaurant", "public"}


class CategoryVote(BaseModel):
    participant_id: str
    category: str


class PlaceVote(BaseModel):
    participant_id: str
    place_id: str
    place_name: str


def _check(room_id: str):
    if room_id not in rooms_db:
        raise HTTPException(status_code=404, detail="존재하지 않는 방입니다.")


def _tally(votes: dict) -> dict:
    counts: dict[str, int] = {}
    for v in votes.values():
        key = v if isinstance(v, str) else v["place_id"]
        counts[key] = counts.get(key, 0) + 1
    top = max(counts, key=counts.get) if counts else None
    return {"counts": counts, "top": top}


@router.post("/category-votes")
def vote_category(room_id: str, data: CategoryVote):
    _check(room_id)
    if data.category not in ALLOWED:
        raise HTTPException(status_code=400, detail="cafe/restaurant/public 중 하나여야 합니다.")
    category_votes.setdefault(room_id, {})[data.participant_id] = data.category
    return _tally(category_votes[room_id])


@router.get("/category-votes")
def get_category_votes(room_id: str):
    _check(room_id)
    return _tally(category_votes.get(room_id, {}))


@router.post("/place-votes")
def vote_place(room_id: str, data: PlaceVote):
    _check(room_id)
    place_votes.setdefault(room_id, {})[data.participant_id] = {
        "place_id": data.place_id,
        "place_name": data.place_name,
    }
    return _tally(place_votes[room_id])


@router.get("/place-votes")
def get_place_votes(room_id: str):
    _check(room_id)
    return _tally(place_votes.get(room_id, {}))
