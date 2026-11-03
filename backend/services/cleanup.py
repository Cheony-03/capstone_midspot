from datetime import datetime, timedelta
from db import rooms_db, participants_db

# 방 만료 기준 (미정이면 24시간으로 두고 나중에 조정)
ROOM_TTL_HOURS = 24


def is_expired(created_at: datetime, now: datetime | None = None) -> bool:
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
