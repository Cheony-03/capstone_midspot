from datetime import datetime, timedelta
from typing import Optional  # 👈 Optional 추가
from db import rooms_db, participants_db

ROOM_TTL_HOURS = 24

def is_expired(created_at: datetime, now: Optional[datetime] = None) -> bool: # 👈 수정
    now = now or datetime.now()
    return now - created_at > timedelta(hours=ROOM_TTL_HOURS)

def cleanup_expired_rooms() -> list[str]:
    """만료된 방과 그 방의 참여자 데이터를 삭제하고 삭제된 room_id 목록을 반환한다."""
    now = datetime.now()
    expired = [rid for rid, room in rooms_db.items() if is_expired(room.created_at, now)]

    for rid in expired:
        rooms_db.pop(rid, None)
        participants_db.pop(rid, None)

    return expired
