from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import applicants, evaluation, interview, batch, calendar, criteria, stages
from app.utils.config import settings

app = FastAPI(
    title="採用書類選考API",
    description="マインドセット評価を中心とした採用プロセス自動化システム",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],  # React開発サーバー
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIルート登録
app.include_router(applicants.router, prefix="/api/applicants", tags=["applicants"])
app.include_router(evaluation.router, prefix="/api/evaluation", tags=["evaluation"])
app.include_router(interview.router, prefix="/api/interview", tags=["interview"])
app.include_router(batch.router, prefix="/api/batch", tags=["batch"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"])
app.include_router(criteria.router, prefix="/api/criteria", tags=["criteria"])
app.include_router(stages.router, prefix="/api/stages", tags=["stages"])

@app.get("/")
async def root():
    return {
        "message": "採用書類選考API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
