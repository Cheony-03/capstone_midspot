from pydantic import BaseModel, Field


class ParticipantCreate(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=20)
    address_name: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class Participant(ParticipantCreate):
    participant_id: str
    room_id: str
