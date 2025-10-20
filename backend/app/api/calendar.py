from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from app.services.calendar_service import CalendarService
from app.utils.supabase_client import get_supabase

router = APIRouter()

calendar_service = CalendarService()

class CreateInterviewRequest(BaseModel):
    applicant_id: str
    start_time: datetime
    duration_minutes: int = 60
    description: Optional[str] = ""

class FindSlotsRequest(BaseModel):
    start_date: datetime
    end_date: datetime
    duration_minutes: int = 60

class UpdateInterviewRequest(BaseModel):
    event_id: str
    start_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    description: Optional[str] = None

@router.post("/create-interview")
async def create_interview_event(request: CreateInterviewRequest):
    """
    面接イベントを作成してGoogleカレンダーに追加

    Args:
        request: 面接イベント作成リクエスト

    Returns:
        作成されたイベント情報
    """
    try:
        supabase = get_supabase()

        # 応募者情報を取得
        applicant_response = supabase.table("applicants").select("*").eq("id", request.applicant_id).execute()

        if not applicant_response.data:
            raise HTTPException(status_code=404, detail="Applicant not found")

        applicant = applicant_response.data[0]

        # カレンダーイベント作成
        result = calendar_service.create_interview_event(
            applicant_name=applicant["name"],
            applicant_email=applicant["email"],
            start_time=request.start_time,
            duration_minutes=request.duration_minutes,
            description=request.description or f"応募者: {applicant['name']}\nメール: {applicant['email']}"
        )

        if not result['success']:
            raise HTTPException(status_code=500, detail=result.get('error'))

        # 応募者データに面接情報を保存
        interview_data = {
            'calendar_event_id': result['event_id'],
            'interview_scheduled_at': request.start_time.isoformat(),
            'interview_duration_minutes': request.duration_minutes,
            'status': 'interview'
        }

        supabase.table("applicants").update(interview_data).eq("id", request.applicant_id).execute()

        return {
            'message': 'Interview scheduled successfully',
            'event_id': result['event_id'],
            'event_link': result['event_link'],
            'start_time': result['start_time'],
            'end_time': result['end_time']
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/find-available-slots")
async def find_available_slots(request: FindSlotsRequest):
    """
    空き時間スロットを検索

    Args:
        request: 検索リクエスト

    Returns:
        空き時間スロットのリスト
    """
    try:
        slots = calendar_service.find_available_slots(
            start_date=request.start_date,
            end_date=request.end_date,
            duration_minutes=request.duration_minutes
        )

        return {
            'count': len(slots),
            'slots': slots
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/update-interview")
async def update_interview_event(request: UpdateInterviewRequest):
    """
    面接イベントを更新

    Args:
        request: 更新リクエスト

    Returns:
        更新結果
    """
    try:
        result = calendar_service.update_interview_event(
            event_id=request.event_id,
            start_time=request.start_time,
            duration_minutes=request.duration_minutes,
            description=request.description
        )

        if not result['success']:
            raise HTTPException(status_code=500, detail=result.get('error'))

        return {
            'message': 'Interview updated successfully',
            'event_id': result['event_id'],
            'event_link': result['event_link']
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cancel-interview/{event_id}")
async def cancel_interview_event(event_id: str):
    """
    面接イベントをキャンセル

    Args:
        event_id: イベントID

    Returns:
        キャンセル結果
    """
    try:
        result = calendar_service.cancel_interview_event(event_id)

        if not result['success']:
            raise HTTPException(status_code=500, detail=result.get('error'))

        return {
            'message': 'Interview cancelled successfully'
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
