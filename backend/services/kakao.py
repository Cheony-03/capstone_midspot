import math
import os
import httpx
from dotenv import load_dotenv

# .env 파일 내 환경 변수(KAKAO_REST_API_KEY) 로드함
load_dotenv()

# 카카오 REST API 키 및 기본 URL 설정함
KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")
BASE_URL = "https://dapi.kakao.com/v2/local"

# API 인증 헤더 설정함
HEADERS = {
    "Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"
}


async def search_address(query: str):
    """
    [기능] 입력받은 주소/지명을 좌표(경도 x, 위도 y)로 변환함.
    
    :param query: 검색할 주소/장소명 (예: "강남역")
    :return: 주소명 및 좌표 리스트 반환함
    """
    url = f"{BASE_URL}/search/address.json"
    params = {"query": query}
    
    # 비동기 HTTP 클라이언트로 카카오 API에 요청 보냄
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS, params=params)
        response.raise_for_status()  # 에러 발생 시 예외 던짐
        data = response.json()
        
        results = []
        # 검색 결과(documents) 파싱 및 정리함
        for doc in data.get("documents", []):
            results.append({
                "address_name": doc["address_name"],  # 전체 주소
                "x": float(doc["x"]),                 # 경도 (Longitude)
                "y": float(doc["y"])                  # 위도 (Latitude)
            })
        return results


def _haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """두 좌표 사이 거리(m)를 계산함."""
    r = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _offset_point(lat: float, lng: float, distance_m: float, bearing_deg: float):
    """기준 좌표에서 지정 방향으로 distance_m 만큼 떨어진 좌표를 구함."""
    r = 6371000
    br = math.radians(bearing_deg)
    p1 = math.radians(lat)
    l1 = math.radians(lng)
    dr = distance_m / r
    p2 = math.asin(math.sin(p1) * math.cos(dr) + math.cos(p1) * math.sin(dr) * math.cos(br))
    l2 = l1 + math.atan2(
        math.sin(br) * math.sin(dr) * math.cos(p1),
        math.cos(dr) - math.sin(p1) * math.sin(p2),
    )
    return math.degrees(p2), math.degrees(l2)


async def _fetch_category_pages(client, lat, lng, category_code, radius, max_pages=3):
    """카카오 카테고리 검색을 페이지 단위로 호출해 최대 max_pages*15 건을 모음."""
    url = f"{BASE_URL}/search/category.json"
    base_params = {
        "category_group_code": category_code,
        "x": str(lng),
        "y": str(lat),
        "radius": radius,
        "sort": "distance",
        "size": 15,
    }

    places = []
    for page in range(1, max_pages + 1):
        params = dict(base_params, page=page)
        response = await client.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()

        documents = data.get("documents", [])
        for doc in documents:
            places.append({
                "place_name": doc["place_name"],
                "address_name": doc["address_name"],
                "road_address_name": doc["road_address_name"],
                "place_url": doc["place_url"],
                "x": float(doc["x"]),
                "y": float(doc["y"]),
                "distance": int(doc["distance"])
            })

        if len(documents) < 15 or data.get("meta", {}).get("is_end", True):
            break

    return places


async def search_places(lat: float, lng: float, category_code: str, radius: int = 1000):
    """
    [기능] 기준 좌표(lat, lng) 주변 반경(radius) 내 특정 카테고리 장소를 검색함.

    :param lat: 위도
    :param lng: 경도
    :param category_code: 카카오 카테고리 그룹 코드 (CE7 카페 / FD6 식당 / SW8 공공장소 등)
    :param radius: 검색 반경 (m 단위, 기본 1000m)
    :return: 주변 장소 목록 반환함
    """
    async with httpx.AsyncClient() as client:
        places = await _fetch_category_pages(client, lat, lng, category_code, radius)

        # 카카오는 최대 45건까지만 주므로 반경을 넓혀도 가까운 곳으로만 채워질 수 있음.
        # 그럴 때는 사방으로 나눠 먼 곳도 함께 모아 반경이 실제로 반영되게 함.
        farthest = max((p["distance"] for p in places), default=0)
        if radius > 1500 and farthest < radius * 0.6:
            for bearing in (0, 90, 180, 270):
                plat, plng = _offset_point(lat, lng, radius * 0.55, bearing)
                places.extend(
                    await _fetch_category_pages(
                        client, plat, plng, category_code, int(radius * 0.45), max_pages=1
                    )
                )

    merged = {}
    for p in places:
        dist = _haversine_m(lat, lng, p["y"], p["x"])
        if dist > radius:
            continue
        key = (p["place_name"], p["x"], p["y"])
        if key in merged:
            continue
        p["distance"] = int(dist)
        merged[key] = p

    return sorted(merged.values(), key=lambda p: p["distance"])[:100]


async def search_cafes_near_point(x: float, y: float, radius: int = 1000):
    """
    [기능] 기준 좌표(x, y) 주변 반경(radius) 내 카페 목록을 검색함.
    
    :param x: 경도
    :param y: 위도
    :param radius: 검색 반경 (m 단위, 기본 1000m)
    :return: 주변 카페 목록 반환함
    """
    url = f"{BASE_URL}/search/keyword.json"
    params = {
        "query": "카페",          # 검색어 "카페"로 고정함
        "x": str(x),             # 기준점 경도
        "y": str(y),             # 기준점 위도
        "radius": radius,        # 검색 반경
        "sort": "distance"       # 거리순 정렬함
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        
        cafes = []
        for doc in data.get("documents", []):
            cafes.append({
                "place_name": doc["place_name"],                # 카페 이름
                "address_name": doc["address_name"],            # 지번 주소
                "road_address_name": doc["road_address_name"],  # 도로명 주소
                "place_url": doc["place_url"],                  # 카카오맵 URL
                "x": float(doc["x"]),                           # 카페 경도
                "y": float(doc["y"]),                           # 카페 위도
                "distance": int(doc["distance"])                # 거리 (m)
            })
        return cafes
