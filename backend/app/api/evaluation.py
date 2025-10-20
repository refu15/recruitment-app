from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uuid
from app.services.ocr_service import OCRService
from app.services.ai_evaluation_service import AIEvaluationService
from app.models.applicant import ApplicantData, EvaluationResult
from app.utils.supabase_client import get_supabase
from datetime import datetime
import json

router = APIRouter()

# ocr_service = OCRService()
# ai_service = AIEvaluationService()

class ExtractRequest(BaseModel):
    applicant_id: str
    resume_url: str

class EvaluateRequest(BaseModel):
    applicant_id: str
    skill_ratio: Optional[float] = None
    mindset_ratio: Optional[float] = None

class RatioUpdateRequest(BaseModel):
    skill_ratio: float
    mindset_ratio: float

@router.post("/extract-data")
async def extract_applicant_data(request: ExtractRequest):
    raise HTTPException(status_code=503, detail="OCR service is temporarily disabled for local testing.")

@router.post("/evaluate")
async def evaluate_applicant(request: EvaluateRequest):
    raise HTTPException(status_code=503, detail="AI evaluation service is temporarily disabled for local testing.")
    """
    応募者を評価

    1. applicant_dataを取得
    2. AI評価実行
    3. 評価結果をDBに保存
    """
    # try:
    #     supabase = get_supabase()
    #
    #     # 応募者データを取得
    #     applicant_response = supabase.table("applicants").select("*").eq("id", request.applicant_id).execute()
    #
    #     if not applicant_response.data:
    #         raise HTTPException(status_code=404, detail="Applicant not found")
    #
    #     applicant = applicant_response.data[0]
    #
    #     if not applicant.get("applicant_data"):
    #         raise HTTPException(status_code=400, detail="Applicant data not extracted yet")
    #
    #     # ApplicantDataオブジェクトに変換
    #     applicant_data = ApplicantData(**applicant["applicant_data"])
    #
    #     # AI評価実行
    #     evaluation = await ai_service.evaluate_applicant(
    #         applicant_data,
    #         skill_ratio=request.skill_ratio,
    #         mindset_ratio=request.mindset_ratio
    #     )
    #
    #     # 評価結果を保存
    #     update_data = {
    #         "evaluation": evaluation.model_dump(),
    #         "updated_at": datetime.utcnow().isoformat(),
    #         "status": "screening"  # ステータスを「審査中」に更新
    #     }
    #
    #     response = supabase.table("applicants").update(update_data).eq("id", request.applicant_id).execute()
    #
    #     return {
    #         "message": "Evaluation completed successfully",
    #         "evaluation": evaluation
    #     }
    #
    # except HTTPException:
    #     raise
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))

@router.post("/{applicant_id}/update-ratio")
async def update_evaluation_ratio(applicant_id: str, request: RatioUpdateRequest):
    raise HTTPException(status_code=503, detail="AI re-evaluation service is temporarily disabled for local testing.")

class ManualEvaluationItem(BaseModel):
    name: str
    definition: str
    score: int
    memo: str

class ManualEvaluationCreate(BaseModel):
    criteria_filename: str
    evaluation_data: List[ManualEvaluationItem]
    overall_comment: Optional[str] = None

@router.post("/{applicant_id}/manual")
async def save_manual_evaluation(applicant_id: str, evaluation: ManualEvaluationCreate):
    """
    手動での評価結果を保存または更新します。
    """
    try:
        supabase = get_supabase()

        # 既存の評価を探す
        existing_eval = supabase.table("manual_evaluations")\
            .select("id")\
            .eq("applicant_id", applicant_id)\
            .eq("criteria_filename", evaluation.criteria_filename)\
            .execute()

        eval_data = {
            "applicant_id": applicant_id,
            "criteria_filename": evaluation.criteria_filename,
            "evaluation_data": [item.model_dump() for item in evaluation.evaluation_data],
            "overall_comment": evaluation.overall_comment,
            "updated_at": datetime.utcnow().isoformat(),
        }

        if existing_eval.data:
            # 更新
            eval_id = existing_eval.data[0]['id']
            response = supabase.table("manual_evaluations").update(eval_data).eq("id", eval_id).execute()
        else:
            # 新規作成
            eval_data["id"] = str(uuid.uuid4())
            eval_data["created_at"] = datetime.utcnow().isoformat()
            response = supabase.table("manual_evaluations").insert(eval_data).execute()

        return {
            "message": "Manual evaluation saved successfully",
            "data": response.data[0]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def _structure_applicant_data(extracted_text: str) -> ApplicantData:
    """
    抽出されたテキストをGemini APIで構造化データに変換
    """
    from vertexai.generative_models import GenerativeModel
    import vertexai
    from app.utils.config import settings
    import os

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.google_application_credentials
    vertexai.init(project=settings.google_cloud_project_id, location="us-central1")

    model = GenerativeModel("gemini-1.5-flash")

    prompt = f"""
以下は履歴書から抽出されたテキストです。このテキストから応募者情報を構造化してJSON形式で出力してください。

【抽出テキスト】
{extracted_text}

【出力形式】
以下のJSON形式で出力してください：

{{
  "name": "氏名",
  "email": "メールアドレス",
  "phone": "電話番号",
  "education": [
    {{"institution": "学校名", "degree": "学位", "field": "専攻", "year": "卒業年"}}
  ],
  "work_experience": [
    {{"company": "会社名", "position": "役職", "duration": "期間", "description": "業務内容"}}
  ],
  "technical_skills": ["スキル1", "スキル2"],
  "soft_skills": ["スキル1", "スキル2"],
  "certifications": ["資格1", "資格2"],
  "motivation": "志望動機（抽出できた場合）",
  "career_goals": "キャリア目標（抽出できた場合）",
  "additional_info": "その他の情報"
}}

情報が見つからない場合は空配列や空文字列を使用してください。
"""

    try:
        response = model.generate_content(prompt)
        result_text = response.text

        # JSONパース
        if "```json" in result_text:
            json_start = result_text.find("```json") + 7
            json_end = result_text.find("```", json_start)
            result_text = result_text[json_start:json_end].strip()
        elif "```" in result_text:
            json_start = result_text.find("```") + 3
            json_end = result_text.find("```", json_start)
            result_text = result_text[json_start:json_end].strip()

        data = json.loads(result_text)

        # ApplicantDataオブジェクトに変換
        data["extracted_text"] = extracted_text
        data["ocr_confidence"] = 0.9  # 仮の値

        return ApplicantData(**data)

    except Exception as e:
        print(f"データ構造化エラー: {str(e)}")
        # エラー時は最小限のデータを返す
        return ApplicantData(
            name="",
            email="",
            extracted_text=extracted_text,
            ocr_confidence=0.0
        )
