import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from models import Room

router = APIRouter(prefix="/rooms", tags=["Rooms"])

# 메모리 저장소 (서버 실행 중 임시 보관용)
rooms_db: dict[str, Room] = {}


@router.post("", response_model=Room, status_code=201)
def create_room():
    """새로운 모임 방을 생성하고 고유 room_id를 발급합니다."""
    room_id = str(uuid.uuid4())[:8]  # 공유하기 쉬운 8자리 고유 문자열
    new_room = Room(room_id=room_id, created_at=datetime.now())
    rooms_db[room_id] = new_room
    return new_room


@router.get("/{room_id}", response_model=Room)
def get_room(room_id: str):
    """방 존재 여부 및 정보를 조회합니다."""
    if room_id not in rooms_db:
        raise HTTPException(status_code=404, detail="존재하지 않는 방입니다.")
    return rooms_db[room_id]