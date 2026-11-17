from fastapi import APIRouter, HTTPException, Query
from db import rooms_db, participants_db
from services.midpoint import calculate_midpoint
from services.kakao import search_places

router = APIRouter(prefix="/api/rooms/{room_id}", tags=["Result"])

CATEGORY_CODE = {
    "cafe": "CE7",
    "restaurant": "FD6",
    "station_terminal": "SW8",
}

CATEGORY_LABEL = {
    "cafe": "카페",
    "restaurant": "식당",
    "station_terminal": "지하철역",
}

# 조사 처리용 (카페가 / 식당이 / 지하철역이)
CATEGORY_PARTICLE = {
    "cafe": "가",
    "restaurant": "이",
    "station_terminal": "이",
}

# 반경을 넓혀가며 찾는 상한과, 그래도 없을 때 "가장 가까운 곳"을 찾는 상한 (카카오 최대 20km)
MAX_RADIUS = 10000
NEAREST_RADIUS = 20000


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
        raise HTTPException(status_code=400, detail="cafe/restaurant/station_terminal 중 하나여야 합니다.")

    mid = calculate_midpoint([(p.latitude, p.longitude) for p in people])

    # 카카오 장소 검색 - 실패 시에도 중간지점은 반환 (API 키 누락 등 대응)
    # 산술평균 중간지점이 상권 밖(빈 지대)에 떨어질 수 있어, 결과가 0건이면 반경을 넓혀 재검색함
    places = []
    search_error = None
    used_radius = radius
    fallback = False
    fallback_category = None
    message = None
    label = CATEGORY_LABEL[category]
    particle = CATEGORY_PARTICLE[category]
    try:
        places = await search_places(
            lat=mid["latitude"],
            lng=mid["longitude"],
            category_code=CATEGORY_CODE[category],
            radius=used_radius,
        )
        while not places and used_radius < MAX_RADIUS:
            used_radius = min(used_radius * 2, MAX_RADIUS)
            places = await search_places(
                lat=mid["latitude"],
                lng=mid["longitude"],
                category_code=CATEGORY_CODE[category],
                radius=used_radius,
            )

        # 반경을 최대한 넓혀도 없으면, 거리순 정렬로 가장 가까운 곳을 안내함
        if not places:
            fallback = True
            used_radius = NEAREST_RADIUS
            places = await search_places(
                lat=mid["latitude"],
                lng=mid["longitude"],
                category_code=CATEGORY_CODE[category],
                radius=used_radius,
            )
            if places:
                nearest = places[0]
                message = (
                    f"주변 {MAX_RADIUS // 1000}km 안에 {label}{particle} 없어 "
                    f"가장 가까운 {label}({nearest['place_name']}, 약 {nearest['distance'] / 1000:.1f}km)부터 보여드립니다."
                )
            else:
                # 선택한 카테고리가 20km 안에 없으면 다른 카테고리에서 가장 가까운 곳을 대신 보여줌
                for other in CATEGORY_CODE:
                    if other == category:
                        continue
                    other_places = await search_places(
                        lat=mid["latitude"],
                        lng=mid["longitude"],
                        category_code=CATEGORY_CODE[other],
                        radius=NEAREST_RADIUS,
                    )
                    if other_places:
                        places = other_places
                        fallback_category = other
                        nearest = other_places[0]
                        message = (
                            f"주변 {NEAREST_RADIUS // 1000}km 안에 {label}{particle} 없어 "
                            f"가장 가까운 {CATEGORY_LABEL[other]}({nearest['place_name']}, "
                            f"약 {nearest['distance'] / 1000:.1f}km)을(를) 대신 보여드립니다."
                        )
                        break
                if not places:
                    message = f"주변 {NEAREST_RADIUS // 1000}km 안에 {label}{particle} 없습니다."
    except Exception as e:
        places = []
        search_error = f"장소 검색 실패: {str(e)} (KAKAO_REST_API_KEY 확인 필요)"

    return {
        "room_id": room_id,
        "participant_count": len(people),
        "midpoint": mid,
        "category": category,
        "radius": used_radius,
        "places": places,
        "fallback": fallback,
        "fallback_category": fallback_category,
        "message": message,
        "search_error": search_error,
    }
