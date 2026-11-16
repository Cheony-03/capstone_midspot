# 인메모리 저장소 (공용). 요청 시 접근하는 모듈은 여기서 참조한다.
from threading import RLock

from models import Room
from schemas import Participant

# 여러 참여자가 동시에 투표해도 집계가 꼬이지 않도록 하는 공용 락
db_lock = RLock()

# 방 목록: room_id -> Room
rooms_db: dict[str, Room] = {}

# 방 별 참여자 목록: room_id -> list[Participant]
participants_db: dict[str, list[Participant]] = {}

# 방 별 카테고리 투표: room_id -> {participant_id: category}
category_votes_db: dict[str, dict[str, str]] = {}

# 방 별 장소 투표: room_id -> {participant_id: {"place_id", "place_name"}}
place_votes_db: dict[str, dict[str, dict]] = {}
