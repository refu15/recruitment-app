from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Dict, Any
from app.services.ai_evaluation_service import AIEvaluationService
from app.models.applicant import ApplicantData, ApplicationStatus
from app.utils.supabase_client import get_supabase
from datetime import datetime
import csv
import io
import uuid
from pydantic import BaseModel

router = APIRouter()

ai_service = AIEvaluationService()

class BatchEvaluationResult(BaseModel):
    total_count: int
    success_count: int
    error_count: int
    results: List[Dict[str, Any]]

@router.post("/upload-csv", response_model=BatchEvaluationResult)
async def batch_process_applicants(
    file: UploadFile = File(...),
    skill_ratio: float = 0.2,
    mindset_ratio: float = 0.8
):
    """
    CSVから複数の応募者を一括処理

    CSVフォーマット:
    name, email, phone, education, work_experience, technical_skills, motivation, career_goals
    """
    try:
        # CSVファイルを読み込み
        contents = await file.read()
        csv_text = contents.decode("utf-8")
        csv_reader = csv.DictReader(io.StringIO(csv_text))

        supabase = get_supabase()

        results = []
        success_count = 0
        error_count = 0

        for row in csv_reader:
            try:
                # ApplicantDataオブジェクトを作成
                applicant_data = _csv_row_to_applicant_data(row)

                # AI評価実行
                evaluation = await ai_service.evaluate_applicant(
                    applicant_data,
                    skill_ratio=skill_ratio,
                    mindset_ratio=mindset_ratio
                )

                # DBに保存
                applicant_id = str(uuid.uuid4())
                applicant_record = {
                    "id": applicant_id,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "name": applicant_data.name,
                    "email": applicant_data.email,
                    "phone": applicant_data.phone,
                    "applicant_data": applicant_data.model_dump(),
                    "evaluation": evaluation.model_dump(),
                    "status": ApplicationStatus.SCREENING.value
                }

                response = supabase.table("applicants").insert(applicant_record).execute()

                results.append({
                    "name": applicant_data.name,
                    "email": applicant_data.email,
                    "status": "success",
                    "applicant_id": applicant_id,
                    "total_score": evaluation.total_score
                })

                success_count += 1

            except Exception as e:
                results.append({
                    "name": row.get("name", "Unknown"),
                    "email": row.get("email", "Unknown"),
                    "status": "error",
                    "error": str(e)
                })
                error_count += 1

        return BatchEvaluationResult(
            total_count=len(results),
            success_count=success_count,
            error_count=error_count,
            results=results
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export-results")
async def export_evaluation_results(
    status: str = None,
    min_score: float = None
):
    """
    評価結果をエクスポート（CSV形式）

    Args:
        status: フィルタするステータス（オプション）
        min_score: 最小スコア（オプション）
    """
    try:
        supabase = get_supabase()

        query = supabase.table("applicants").select("*")

        if status:
            query = query.eq("status", status)

        response = query.execute()

        # CSVデータを構築
        csv_data = []
        for applicant in response.data:
            evaluation = applicant.get("evaluation")
            if evaluation:
                total_score = evaluation.get("total_score", 0)

                # min_scoreフィルタ
                if min_score and total_score < min_score:
                    continue

                csv_data.append({
                    "ID": applicant["id"],
                    "名前": applicant["name"],
                    "メール": applicant["email"],
                    "ステータス": applicant["status"],
                    "総合スコア": total_score,
                    "スキルスコア": evaluation.get("skill_score", 0),
                    "マインドセットスコア": evaluation.get("mindset_score", 0),
                    "評価サマリー": evaluation.get("summary", ""),
                    "作成日時": applicant["created_at"]
                })

        return {
            "count": len(csv_data),
            "data": csv_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ヘルパー関数
def _csv_row_to_applicant_data(row: Dict[str, str]) -> ApplicantData:
    """CSV行をApplicantDataオブジェクトに変換"""

    # カンマ区切りのリストを配列に変換
    technical_skills = [s.strip() for s in row.get("technical_skills", "").split(",") if s.strip()]
    soft_skills = [s.strip() for s in row.get("soft_skills", "").split(",") if s.strip()]

    # 学歴・職歴はJSON形式またはテキスト形式で受け取る想定
    education = []
    if row.get("education"):
        try:
            import json
            education = json.loads(row["education"])
        except:
            education = [{"institution": row["education"]}]

    work_experience = []
    if row.get("work_experience"):
        try:
            import json
            work_experience = json.loads(row["work_experience"])
        except:
            work_experience = [{"company": row["work_experience"]}]

    return ApplicantData(
        name=row.get("name", ""),
        email=row.get("email", ""),
        phone=row.get("phone"),
        education=education,
        work_experience=work_experience,
        technical_skills=technical_skills,
        soft_skills=soft_skills,
        certifications=[],
        motivation=row.get("motivation", ""),
        career_goals=row.get("career_goals", ""),
        additional_info=row.get("additional_info", "")
    )
