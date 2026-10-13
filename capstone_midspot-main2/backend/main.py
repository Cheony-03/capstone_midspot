from fastapi import FastAPI
from routers import rooms, participants

app = FastAPI(title="MidSpot API", version="0.1.0")

# 라우터 등록
app.include_router(rooms.router)
app.include_router(participants.router)


@app.get("/")
def root():
    return {"message": "MidSpot Backend is running"}