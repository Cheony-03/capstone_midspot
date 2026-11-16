from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import (
    rooms_db,
    participants_db,
    category_votes_db,
    place_votes_db,
    db_lock,
)

router = APIRouter(prefix="/api/rooms/{room_id}", tags=["Votes"])

ALLOWED = {"cafe", "restaurant", "station_terminal"}


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


def _check_participant(room_id: str, participant_id: str):
    ids = {p.participant_id for p in participants_db.get(room_id, [])}
    if participant_id not in ids:
        raise HTTPException(status_code=403, detail="이 방의 참여자가 아닙니다. 출발지를 먼저 입력해주세요.")


def _tally(votes: dict) -> dict:
    counts: dict[str, int] = {}
    for v in votes.values():
        key = v if isinstance(v, str) else v["place_id"]
        counts[key] = counts.get(key, 0) + 1

    top = None
    tied = False
    if counts:
        best = max(counts.values())
        leaders = [k for k, c in counts.items() if c == best]
        top = leaders[0]
        tied = len(leaders) > 1
    return {
        "counts": counts,
        "top": top,
        "top_count": counts.get(top, 0) if top else 0,
        "tied": tied,
        "total_votes": len(votes),
    }


@router.post("/category-votes")
def vote_category(room_id: str, data: CategoryVote):
    _check(room_id)
    if data.category not in ALLOWED:
        raise HTTPException(status_code=400, detail="cafe/restaurant/station_terminal 중 하나여야 합니다.")
    _check_participant(room_id, data.participant_id)
    with db_lock:
        category_votes_db.setdefault(room_id, {})[data.participant_id] = data.category
        return _tally(category_votes_db[room_id])


@router.get("/category-votes")
def get_category_votes(room_id: str):
    _check(room_id)
    with db_lock:
        return _tally(category_votes_db.get(room_id, {}))


@router.post("/place-votes")
def vote_place(room_id: str, data: PlaceVote):
    _check(room_id)
    _check_participant(room_id, data.participant_id)
    with db_lock:
        place_votes_db.setdefault(room_id, {})[data.participant_id] = {
            "place_id": data.place_id,
            "place_name": data.place_name,
        }
        return _tally(place_votes_db[room_id])


@router.get("/place-votes")
def get_place_votes(room_id: str):
    _check(room_id)
    with db_lock:
        return _tally(place_votes_db.get(room_id, {}))


@router.get("/place-votes/winner")
def get_winner_place(room_id: str):
    _check(room_id)
    with db_lock:
        votes = dict(place_votes_db.get(room_id, {}))
        total_participants = len(participants_db.get(room_id, []))

    if not votes:
        raise HTTPException(status_code=404, detail="아직 장소 투표가 없습니다.")

    result = _tally(votes)
    winner_id = result["top"]
    winner_name = next(
        (v["place_name"] for v in votes.values() if v["place_id"] == winner_id),
        winner_id,
    )
    return {
        "place_id": winner_id,
        "place_name": winner_name,
        "votes": result["top_count"],
        "tied": result["tied"],
        "total_votes": result["total_votes"],
        "participant_count": total_participants,
        "counts": result["counts"],
    }
