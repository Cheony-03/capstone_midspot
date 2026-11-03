# 인메모리 저장소 (공용). 요청 시 접근하는 모듈은 여기서 참조한다.
from models import Room
from schemas import Participant

# 방 목록: room_id -> Room
rooms_db: dict[str, Room] = {}

# 방 별 참여자 목록: room_id -> list[Participant]
participants_db: dict[str, list[Participant]] = {}
