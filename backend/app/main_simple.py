from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="採用書類選考API",
    description="マインドセット評価を中心とした採用プロセス自動化システム",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "採用書類選考API",
        "version": "1.0.0",
        "docs": "/docs",
        "note": "Google Cloud認証情報を設定してフル機能を使用してください"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
