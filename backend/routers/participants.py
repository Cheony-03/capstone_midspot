import uuid
from fastapi import APIRouter, Header, HTTPException
from schemas import ParticipantCreate, Participant
from db import rooms_db, participants_db, category_votes_db, place_votes_db, db_lock

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
    with db_lock:
        current_list.append(new_participant)
    return new_participant


@router.get("", response_model=list[Participant])
def get_participants(room_id: str):
    if room_id not in rooms_db:
        raise HTTPException(status_code=404, detail="존재하지 않는 방입니다.")
    return participants_db.get(room_id, [])


@router.delete("/{participant_id}")
def delete_participant(room_id: str, participant_id: str, x_host_token: str = Header(default="")):
    """방장만 참여자의 출발지 정보를 삭제할 수 있다."""
    if room_id not in rooms_db:
        raise HTTPException(status_code=404, detail="존재하지 않는 방입니다.")

    if not x_host_token or x_host_token != rooms_db[room_id].host_token:
        raise HTTPException(status_code=403, detail="방장만 참여자를 삭제할 수 있습니다.")

    with db_lock:
        current_list = participants_db.get(room_id, [])
        target = next((p for p in current_list if p.participant_id == participant_id), None)
        if target is None:
            raise HTTPException(status_code=404, detail="존재하지 않는 참여자입니다.")

        current_list.remove(target)
        category_votes_db.get(room_id, {}).pop(participant_id, None)
        place_votes_db.get(room_id, {}).pop(participant_id, None)

    return {"deleted": participant_id}
