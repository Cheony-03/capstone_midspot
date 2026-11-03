from fastapi import APIRouter, HTTPException, Query
from db import rooms_db, participants_db
from services.midpoint import calculate_midpoint
from services.kakao import search_places

router = APIRouter(prefix="/api/rooms/{room_id}", tags=["Result"])

# 카카오 카테고리 코드
CATEGORY_CODE = {
    "cafe": "CE7",
    "restaurant": "FD6",
    "public": "SW8",
}


@router.get("/result")
async def get_result(
    room_id: str,
    category: str = Query("cafe"),
    radius: int = Query(1000, ge=100, le=5000),
):
    if room_id not in rooms_db:
        raise HTTPException(status_code=404, detail="존재하지 않는 방입니다.")

    people = participants_db.get(room_id, [])
    if len(people) < 2:
        raise HTTPException(status_code=400, detail="참여자가 2명 이상이어야 중간지점을 계산할 수 있습니다.")

    if category not in CATEGORY_CODE:
        raise HTTPException(status_code=400, detail="cafe/restaurant/public 중 하나여야 합니다.")

    mid = calculate_midpoint([(p.latitude, p.longitude) for p in people])

    # 카카오 장소 검색 - 실패 시에도 중간지점은 반환 (API 키 누락 등 대응)
    try:
        places = await search_places(
            lat=mid["latitude"],
            lng=mid["longitude"],
            category_code=CATEGORY_CODE[category],
            radius=radius,
        )
        search_error = None
    except Exception as e:
        places = []
        search_error = f"장소 검색 실패: {str(e)} (KAKAO_REST_API_KEY 확인 필요)"

    return {
        "room_id": room_id,
        "participant_count": len(people),
        "midpoint": mid,
        "category": category,
        "radius": radius,
        "places": places,
        "search_error": search_error,
    }