import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from models import Room, RoomPublic
from db import rooms_db
from services.cleanup import cleanup_expired_rooms

router = APIRouter(prefix="/api/rooms", tags=["Rooms"])


@router.post("", response_model=Room, status_code=201)
def create_room():
    room_id = str(uuid.uuid4())[:8]
    new_room = Room(room_id=room_id, created_at=datetime.now(), host_token=uuid.uuid4().hex)
    rooms_db[room_id] = new_room
    return new_room


@router.get("/{room_id}", response_model=RoomPublic)
def get_room(room_id: str):
    if room_id not in rooms_db:
        raise HTTPException(status_code=404, detail="존재하지 않는 방입니다.")
    return rooms_db[room_id]


@router.delete("/cleanup")
def cleanup():
    return {"deleted": cleanup_expired_rooms()}
