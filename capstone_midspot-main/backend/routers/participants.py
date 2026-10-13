import uuid
from fastapi import APIRouter, HTTPException
from schemas import ParticipantCreate, Participant
from routers.rooms import rooms_db

router = APIRouter(prefix="/rooms/{room_id}/participants", tags=["Participants"])

# 메모리 저장소: {room_id: [Participant, ...]}
participants_db: dict[str, list[Participant]] = {}


@router.post("", response_model=Participant, status_code=201)
def add_participant(room_id: str, data: ParticipantCreate):
    """특정 방에 참여자 정보를 등록합니다."""
    # 1. 방 존재 여부 확인
    if room_id not in rooms_db:
        raise HTTPException(status_code=404, detail="존재하지 않는 방입니다.")

    if room_id not in participants_db:
        participants_db[room_id] = []

    # 2. 방 내 닉네임 중복 검사
    current_list = participants_db[room_id]
    if any(p.nickname == data.nickname for p in current_list):
        raise HTTPException(status_code=400, detail="이미 사용 중인 닉네임입니다.")

    # 3. 참여자 생성 및 저장
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
    """해당 방에 등록된 모든 참여자 목록을 조회합니다."""
    if room_id not in rooms_db:
        raise HTTPException(status_code=404, detail="존재하지 않는 방입니다.")
    return participants_db.get(room_id, [])