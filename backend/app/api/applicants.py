from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
from app.models.applicant import Applicant, ApplicantCreate, ApplicantUpdate, ApplicationStatus
from app.utils.supabase_client import get_supabase
from datetime import datetime
import uuid

router = APIRouter()

@router.get("/", response_model=List[Applicant])
async def get_applicants(
    status: Optional[ApplicationStatus] = None,
    limit: int = 100,
    offset: int = 0
):
    """応募者一覧を取得"""
    try:
        supabase = get_supabase()

        query = supabase.table("applicants").select("*")

        if status:
            query = query.eq("status", status.value)

        response = query.range(offset, offset + limit - 1).execute()

        return response.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{applicant_id}", response_model=Applicant)
async def get_applicant(applicant_id: str):
    """特定の応募者を取得"""
    try:
        response = supabase.table("applicants").select("*").eq("id", applicant_id).single().execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Applicant not found")

        return response.data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Applicant)
async def create_applicant(applicant: ApplicantCreate):
    """応募者を新規作成"""
    try:
        supabase = get_supabase()

        applicant_data = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "name": applicant.name,
            "email": applicant.email,
            "phone": applicant.phone,
            "resume_url": applicant.resume_url,
            "cover_letter": applicant.cover_letter,
            "status": ApplicationStatus.PENDING.value
        }

        response = supabase.table("applicants").insert(applicant_data).execute()

        return response.data[0]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{applicant_id}", response_model=Applicant)
async def update_applicant(applicant_id: str, update_data: ApplicantUpdate):
    """応募者情報を更新"""
    try:
        supabase = get_supabase()

        # 更新データを準備（Noneでない項目のみ）
        update_dict = {
            "updated_at": datetime.utcnow().isoformat()
        }

        if update_data.name is not None:
            update_dict["name"] = update_data.name
        if update_data.email is not None:
            update_dict["email"] = update_data.email
        if update_data.phone is not None:
            update_dict["phone"] = update_data.phone
        if update_data.status is not None:
            update_dict["status"] = update_data.status.value
        if update_data.notes is not None:
            update_dict["notes"] = update_data.notes
        if update_data.tags is not None:
            update_dict["tags"] = update_data.tags

        response = supabase.table("applicants").update(update_dict).eq("id", applicant_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Applicant not found")

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{applicant_id}")
async def delete_applicant(applicant_id: str):
    """応募者を削除"""
    try:
        supabase = get_supabase()

        response = supabase.table("applicants").delete().eq("id", applicant_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Applicant not found")

        return {"message": "Applicant deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{applicant_id}/upload-resume")
async def upload_resume(applicant_id: str, file: UploadFile = File(...)):
    """履歴書PDFをアップロード"""
    try:
        supabase = get_supabase()

        # ファイルを読み込み
        contents = await file.read()

        # Supabase Storageにアップロード
        file_path = f"resumes/{applicant_id}/{file.filename}"
        storage_response = supabase.storage.from_("applicant-documents").upload(
            file_path,
            contents,
            {"content-type": file.content_type}
        )

        # 公開URLを取得
        public_url = supabase.storage.from_("applicant-documents").get_public_url(file_path)

        # 応募者情報を更新
        update_response = supabase.table("applicants").update({
            "resume_url": public_url,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", applicant_id).execute()

        return {
            "message": "Resume uploaded successfully",
            "url": public_url
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
