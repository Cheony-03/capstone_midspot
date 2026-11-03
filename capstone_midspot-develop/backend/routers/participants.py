import uuid
from fastapi import APIRouter, HTTPException
from schemas import ParticipantCreate, Participant
from db import rooms_db, participants_db

router = APIRouter(prefix="/api/rooms/{room_id}/participants", tags=["Participants"])


@router.post("", response_model=Participant, status_code=201)
def add_participant(room_id: str, data: ParticipantCreate):
    if room_id not in rooms_db:
        raise HTTPException(status_code=404, detail="존재하지 않는 방입니다.")

    if room_id not in participants_db:
        participants_db[room_id] = []

    current_list = participants_db[room_id]
    if any(p.nickname == data.nickname for p in current_list):
        raise HTTPException(status_code=400, detail="이미 사용 중인 닉네임입니다.")

    new_participant = Participant(
        participant_id=str(uuid.uuid4())[:8],
        room_id=room_id,
        nickname=data.nickname,
        address_name=data.address_name,
        latitude=data.latitude,
        longitude=data.longitude,
    )
    current_list.append(new_participant)
    return new_participant


@router.get("", response_model=list[Participant])
def get_participants(room_id: str):
    if room_id not in rooms_db:
        raise HTTPException(status_code=404, detail="존재하지 않는 방입니다.")
    return participants_db.get(room_id, [])
