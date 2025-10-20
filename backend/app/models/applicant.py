from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ApplicationStatus(str, Enum):
    PENDING = "pending"
    SCREENING = "screening"
    INTERVIEW = "interview"
    PASSED = "passed"
    REJECTED = "rejected"

class SelectionStage(str, Enum):
    """選考ステージ"""
    DOCUMENT_SCREENING = "document_screening"  # 書類選考
    FIRST_INTERVIEW = "first_interview"        # 一次面接
    SECOND_INTERVIEW = "second_interview"      # 二次面接
    THIRD_INTERVIEW = "third_interview"        # 三次面接
    FINAL_INTERVIEW = "final_interview"        # 最終面接
    OFFER = "offer"                            # 内定
    REJECTED = "rejected"                      # 不合格

class SkillEvaluation(BaseModel):
    category: str
    score: float = Field(..., ge=0, le=10)
    evidence: List[str] = []

class MindsetEvaluation(BaseModel):
    category: str
    score: float = Field(..., ge=0, le=10)
    evidence: List[str] = []

class EvaluationResult(BaseModel):
    skill_evaluations: List[SkillEvaluation] = []
    mindset_evaluations: List[MindsetEvaluation] = []
    skill_score: float = Field(..., ge=0, le=10)
    mindset_score: float = Field(..., ge=0, le=10)
    total_score: float = Field(..., ge=0, le=10)
    skill_ratio: float = Field(0.2, ge=0, le=1)
    mindset_ratio: float = Field(0.8, ge=0, le=1)
    summary: str = ""
    strengths: List[str] = []
    concerns: List[str] = []
    recommended_stage: Optional[SelectionStage] = None  # AI推奨ステージ

class ApplicantCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    resume_url: Optional[str] = None
    cover_letter: Optional[str] = None

class ApplicantData(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    education: List[Dict[str, Any]] = []
    work_experience: List[Dict[str, Any]] = []
    technical_skills: List[str] = []
    soft_skills: List[str] = []
    certifications: List[str] = []
    motivation: str = ""
    career_goals: str = ""
    additional_info: str = ""
    extracted_text: str = ""
    ocr_confidence: float = 0.0

class ManualEvaluationItem(BaseModel):
    name: str
    definition: str
    score: int
    memo: str

class ManualEvaluation(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    applicant_id: str
    criteria_filename: str
    evaluation_data: List[ManualEvaluationItem]
    overall_comment: Optional[str] = None

class Applicant(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    name: str
    email: str
    phone: Optional[str] = None
    resume_url: Optional[str] = None
    cover_letter: Optional[str] = None
    applicant_data: Optional[ApplicantData] = None
    evaluation: Optional[EvaluationResult] = None
    status: ApplicationStatus = ApplicationStatus.PENDING
    
    # 選考ステージ管理
    current_stage: SelectionStage = SelectionStage.DOCUMENT_SCREENING
    stage_history: List[Dict[str, Any]] = []  # ステージ履歴
    
    interview_questions: List[str] = []
    interview_transcript: Optional[str] = None
    interview_summary: Optional[str] = None
    tags: List[str] = []
    notes: str = ""
    manual_evaluations: List[ManualEvaluation] = []

class ApplicantUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[ApplicationStatus] = None
    current_stage: Optional[SelectionStage] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None

class FileUploadResponse(BaseModel):
    """ファイルアップロードレスポンス"""
    success: bool
    applicant_id: Optional[str] = None
    file_type: str
    extracted_data: Optional[ApplicantData] = None
    ai_recommendation: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
