from pydantic import BaseModel, Field


class ParticipantCreate(BaseModel):
    """참여자 등록 요청 (프론트 -> 서버)"""
    nickname: str = Field(..., min_length=1, max_length=20)
    address_name: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class Participant(ParticipantCreate):
    """참여자 조회 응답"""
    participant_id: str
    room_id: str