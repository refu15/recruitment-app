from fastapi import APIRouter, HTTPException
from typing import List
import uuid
from app.models.stage import Stage, StageCreate
from app.utils.supabase_client import get_supabase

router = APIRouter()

@router.get("/", response_model=List[Stage])
async def get_all_stages():
    """定義済みのすべての選考ステージを取得します。"""
    try:
        supabase = get_supabase()
        response = supabase.table("selection_stages").select("*").order("order").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Stage)
async def create_stage(stage: StageCreate):
    """新しい選考ステージを定義します。"""
    try:
        supabase = get_supabase()
        stage_data = stage.model_dump()
        stage_data['id'] = str(uuid.uuid4())
        
        response = supabase.table("selection_stages").insert(stage_data).execute()
        return response.data[0]
    except Exception as e:
        # ユニークキー制約違反などを考慮
        raise HTTPException(status_code=500, detail=str(e))
