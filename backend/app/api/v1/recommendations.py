from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, Record, Profile, Recommendation, Feedback, PublicMetric, Student
from app.schemas.schemas import RecommendationResponse, FeedbackCreate, FeedbackResponse, ProfileResponse
from app.core.errors import EntityNotFoundError, PermissionDeniedError
from app.core.logging import log_audit
from typing import List
import uuid

router = APIRouter()

@router.get("/record/{record_id}", response_model=List[RecommendationResponse])
def get_recommendations(
    request: Request,
    record_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise EntityNotFoundError("해당 생기부 기록을 찾을 수 없습니다.")

    # Validation Owner
    student = db.query(Student).filter(Student.id == record.student_id).first()
    if current_user.role == "student" and student.user_id != current_user.id:
        raise PermissionDeniedError("이 추천 결과에 접근할 권한이 없습니다.")

    profile = db.query(Profile).filter(Profile.record_id == record.id).first()
    if not profile:
        raise EntityNotFoundError("역량 프로파일링이 완료되지 않았습니다.")

    recommendations = db.query(Recommendation).filter(
        Recommendation.profile_id == profile.id
    ).order_by(Recommendation.rank.asc()).all()

    log_audit(db, "VIEW_RECOMMENDATION", "Profile", str(profile.id), user_id=str(current_user.id), ip_address=request.client.host)

    # Transform recommendations and map public metrics evidence details if matched
    response_data = []
    for rec in recommendations:
        evidences_response = []
        for ev in rec.evidences:
            # Map metric detail object if present
            metric_data = None
            if ev.metric_id:
                metric_data = ev.metric
            
            evidences_response.append({
                "id": ev.id,
                "evidence_span": ev.evidence_span,
                "section_type": ev.section_type,
                "evidence_type": ev.evidence_type,
                "relevance_score": ev.relevance_score,
                "metric": metric_data
            })
            
        response_data.append({
            "id": rec.id,
            "rec_type": rec.rec_type,
            "rank": rec.rank,
            "target_name": rec.target_name,
            "score": rec.score,
            "explanation": rec.explanation,
            "action_plan": rec.action_plan,
            "confidence": rec.confidence,
            "evidences": evidences_response
        })

    return response_data

@router.get("/profile/{record_id}", response_model=ProfileResponse)
def get_profile(
    record_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise EntityNotFoundError("기록을 찾을 수 없습니다.")

    student = db.query(Student).filter(Student.id == record.student_id).first()
    if current_user.role == "student" and student.user_id != current_user.id:
        raise PermissionDeniedError("접근할 권한이 없습니다.")

    profile = db.query(Profile).filter(Profile.record_id == record_id).first()
    if not profile:
        raise EntityNotFoundError("역량 분석 결과가 아직 완성되지 않았습니다.")

    return profile

@router.post("/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    request: Request,
    feedback_in: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recommendation = db.query(Recommendation).filter(Recommendation.id == feedback_in.recommendation_id).first()
    if not recommendation:
        raise EntityNotFoundError("해당 추천 리소스를 찾을 수 없습니다.")

    feedback = Feedback(
        user_id=current_user.id,
        recommendation_id=feedback_in.recommendation_id,
        rating=feedback_in.rating,
        comment=feedback_in.comment
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    log_audit(
        db, 
        "SUBMIT_FEEDBACK", 
        "Recommendation", 
        str(recommendation.id), 
        user_id=str(current_user.id), 
        metadata_info={"rating": feedback_in.rating},
        ip_address=request.client.host
    )

    return feedback
