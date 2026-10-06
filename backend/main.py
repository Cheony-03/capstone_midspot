from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import cafes

# FastAPI 앱 생성함
app = FastAPI(
    title="Capstone Midspot API",
    description="중간 지점 및 주변 카페 추천 백엔드 API임",
    version="1.0.0"
)

# CORS 설정 (프론트엔드 통신 허용함)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # 모든 도메인 허용
    allow_credentials=True,
    allow_methods=["*"],        # 모든 HTTP 메서드 허용
    allow_headers=["*"],
)

# 카페 라우터 등록함
app.include_router(cafes.router)


@app.get("/")
def read_root():
    """
    [GET] 서버 정상 동작 확인용 헬스체크임.
    """
    return {"message": "Capstone Midspot API Server is running!"}
