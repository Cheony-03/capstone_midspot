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
