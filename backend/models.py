from datetime import datetime
from pydantic import BaseModel


class Room(BaseModel):
    room_id: str
    created_at: datetime
    host_token: str


class RoomPublic(BaseModel):
    room_id: str
    created_at: datetime
