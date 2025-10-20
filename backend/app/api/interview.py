from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.services.interview_service import InterviewService
from app.models.applicant import ApplicantData, EvaluationResult
from app.utils.supabase_client import get_supabase
from datetime import datetime

router = APIRouter()

interview_service = InterviewService()

class GenerateQuestionsRequest(BaseModel):
    applicant_id: str
    question_count: int = 10

@router.post("/generate-questions")
async def generate_interview_questions(request: GenerateQuestionsRequest):
    """
    一次面接の質問を生成

    マインドセット評価を基に、応募者に適した面接質問を生成
    """
    try:
        supabase = get_supabase()

        # 応募者データを取得
        applicant_response = supabase.table("applicants").select("*").eq("id", request.applicant_id).execute()

        if not applicant_response.data:
            raise HTTPException(status_code=404, detail="Applicant not found")

        applicant = applicant_response.data[0]

        # applicant_dataとevaluationが必要
        if not applicant.get("applicant_data"):
            raise HTTPException(status_code=400, detail="Applicant data not extracted yet")

        if not applicant.get("evaluation"):
            raise HTTPException(status_code=400, detail="Applicant not evaluated yet")

        # オブジェクトに変換
        applicant_data = ApplicantData(**applicant["applicant_data"])
        evaluation = EvaluationResult(**applicant["evaluation"])

        # 質問生成
        questions = await interview_service.generate_interview_questions(
            applicant_data,
            evaluation,
            question_count=request.question_count
        )

        # 質問をDBに保存
        update_data = {
            "interview_questions": questions,
            "updated_at": datetime.utcnow().isoformat(),
            "status": "interview"  # ステータスを「面接」に更新
        }

        response = supabase.table("applicants").update(update_data).eq("id", request.applicant_id).execute()

        return {
            "message": "Interview questions generated successfully",
            "questions": questions
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{applicant_id}/questions")
async def get_interview_questions(applicant_id: str):
    """応募者の面接質問を取得"""
    try:
        supabase = get_supabase()

        applicant_response = supabase.table("applicants").select("interview_questions").eq("id", applicant_id).execute()

        if not applicant_response.data:
            raise HTTPException(status_code=404, detail="Applicant not found")

        questions = applicant_response.data[0].get("interview_questions", [])

        return {
            "questions": questions
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
