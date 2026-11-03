from fastapi import APIRouter, HTTPException
from services.kakao import search_address, search_cafes_near_point

# 카페 관련 API 라우터 객체 생성함
router = APIRouter(prefix="/api/cafes", tags=["cafes"])


@router.get("/search-address")
async def get_address_coordinates(query: str):
    """
    [GET] 주소/장소명 좌표 변환 API임.
    - 예시: /api/cafes/search-address?query=강남역
    """
    try:
        return await search_address(query)
    except Exception as e:
        # 카카오 API 실패(키 누락 401 등) 시 읽을 수 있는 JSON 에러로 반환함
        raise HTTPException(status_code=502, detail=f"주소 검색 실패: {e} (KAKAO_REST_API_KEY 설정 확인 필요)")


@router.get("/search-near")
async def get_cafes_near(x: float, y: float, radius: int = 1000):
    """
    [GET] 지정 좌표 근처 카페 검색 API임.
    - 예시: /api/cafes/search-near?x=127.0276&y=37.4979&radius=1000
    """
    try:
        return await search_cafes_near_point(x, y, radius)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"카페 검색 실패: {e} (KAKAO_REST_API_KEY 설정 확인 필요)")
