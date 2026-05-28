from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from uuid import UUID
from app.models.models import UserRole, RecordStatus, SectionType, RecommendationType, EvidenceType, QualityFlag

# Auth & Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[UserRole] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.STUDENT
    masked_name: str
    grade: str
    school_type: str
    region: str

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True

# Student Schemas
class StudentResponse(BaseModel):
    id: UUID
    user_id: UUID
    masked_name: str
    grade: str
    school_type: str
    region: str
    created_at: datetime

    class Config:
        from_attributes = True

# Record Schemas
class RecordResponse(BaseModel):
    id: UUID
    student_id: UUID
    original_filename: str
    status: RecordStatus
    error_detail: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ParsedSectionResponse(BaseModel):
    id: UUID
    section_type: SectionType
    content: str
    page_number: Optional[int]

    class Config:
        from_attributes = True

# Competency & Profile Schemas
class CompetencyScores(BaseModel):
    탐구력: float = Field(..., ge=0.0, le=100.0)
    협업: float = Field(..., ge=0.0, le=100.0)
    의사소통: float = Field(..., ge=0.0, le=100.0)
    자기주도성: float = Field(..., ge=0.0, le=100.0)

class ProfileResponse(BaseModel):
    id: UUID
    record_id: UUID
    competency_scores: CompetencyScores
    interest_tags: List[str]
    overall_confidence: float

    class Config:
        from_attributes = True

# Public Metrics Schemas
class PublicMetricResponse(BaseModel):
    id: UUID
    source: str
    category: str
    key_name: str
    data: Dict[str, Any]
    reference_year: Optional[date]
    updated_at: datetime
    quality_flag: QualityFlag

    class Config:
        from_attributes = True

# Recommendation Schemas
class RecommendationEvidenceResponse(BaseModel):
    id: UUID
    evidence_span: str
    section_type: Optional[str]
    evidence_type: EvidenceType
    relevance_score: float
    metric: Optional[PublicMetricResponse] = None

    class Config:
        from_attributes = True

class RecommendationResponse(BaseModel):
    id: UUID
    rec_type: RecommendationType
    rank: int
    target_name: str
    score: float
    explanation: str
    action_plan: str
    confidence: float
    evidences: List[RecommendationEvidenceResponse] = []

    class Config:
        from_attributes = True

# Feedback Schemas
class FeedbackCreate(BaseModel):
    recommendation_id: UUID
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: UUID
    user_id: UUID
    recommendation_id: UUID
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Bias Monitoring Schema
class BiasLogResponse(BaseModel):
    school_type: str
    region: str
    recommendations: List[str]
    created_at: datetime
