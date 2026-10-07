from datetime import datetime
from pydantic import BaseModel


class Room(BaseModel):
    """모임 방 (Supabase rooms 테이블과 대응)"""
    room_id: str          # 방 고유 ID
    created_at: datetime  # 방 생성 시각