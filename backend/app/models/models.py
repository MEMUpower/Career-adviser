import uuid
from sqlalchemy import (
    Column, String, ForeignKey, DateTime, Float, Integer, JSON, Text, Enum as SQLEnum, Date
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from pgvector.sqlalchemy import Vector
from app.database import Base

import enum

class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class RecordStatus(str, enum.Enum):
    PENDING = "PENDING"
    PARSING = "PARSING"
    TAGGING = "TAGGING"
    RECOMMENDING = "RECOMMENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class SectionType(str, enum.Enum):
    SUBJECT = "교과"
    SETEUK = "세특"
    CREATIVE = "창체"
    READING = "독서"
    AWARDS = "수상"
    CAREER = "진로활동"

class RecommendationType(str, enum.Enum):
    MAJOR = "전공"
    JOB = "직무군"

class EvidenceType(str, enum.Enum):
    MODEL = "MODEL"
    STATISTIC = "STATISTIC"

class QualityFlag(str, enum.Enum):
    FRESH = "FRESH"
    STALE = "STALE"
    MISSING = "MISSING"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.STUDENT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = relationship("Student", uselist=False, back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

class Student(Base):
    __tablename__ = "students"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    masked_name = Column(String, nullable=False)
    grade = Column(String, nullable=False)
    school_type = Column(String, nullable=False)  # 일반고, 자사고, 특목고 등
    region = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="student")
    records = relationship("Record", back_populates="student", cascade="all, delete-orphan")

class Record(Base):
    __tablename__ = "records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    original_filename = Column(String, nullable=False)
    stored_path = Column(String, nullable=False)
    file_hash = Column(String, unique=True, index=True, nullable=False)
    status = Column(SQLEnum(RecordStatus), default=RecordStatus.PENDING, nullable=False)
    error_detail = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = relationship("Student", back_populates="records")
    parsed_sections = relationship("ParsedSection", back_populates="record", cascade="all, delete-orphan")
    profile = relationship("Profile", uselist=False, back_populates="record", cascade="all, delete-orphan")

class ParsedSection(Base):
    __tablename__ = "parsed_sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    record_id = Column(UUID(as_uuid=True), ForeignKey("records.id", ondelete="CASCADE"), nullable=False)
    section_type = Column(SQLEnum(SectionType), nullable=False)
    content = Column(Text, nullable=False)  # 비식별화 처리된 텍스트
    metadata_info = Column(JSON, name="metadata", nullable=True)
    page_number = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    record = relationship("Record", back_populates="parsed_sections")

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    record_id = Column(UUID(as_uuid=True), ForeignKey("records.id", ondelete="CASCADE"), nullable=False, unique=True)
    competency_scores = Column(JSON, nullable=False)  # 탐구력, 협업, 의사소통, 자기주도성 등
    interest_tags = Column(JSON, nullable=False)
    embedding = Column(Vector(768), nullable=True)  # pgvector 컬럼 (768차원 임베딩 예시)
    overall_confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    record = relationship("Record", back_populates="profile")
    recommendations = relationship("Recommendation", back_populates="profile", cascade="all, delete-orphan")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    rec_type = Column(SQLEnum(RecommendationType), nullable=False)  # 전공 또는 직무군
    rank = Column(Integer, nullable=False)
    target_name = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    explanation = Column(Text, nullable=False)
    action_plan = Column(Text, nullable=False)
    confidence = Column(Float, default=1.0)
    weight_snapshot = Column(JSON, nullable=True)  # 추천 생성 시 적용된 가중치 설정
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("Profile", back_populates="recommendations")
    evidences = relationship("RecommendationEvidence", back_populates="recommendation", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="recommendation", cascade="all, delete-orphan")

class RecommendationEvidence(Base):
    __tablename__ = "recommendation_evidence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recommendation_id = Column(UUID(as_uuid=True), ForeignKey("recommendations.id", ondelete="CASCADE"), nullable=False)
    metric_id = Column(UUID(as_uuid=True), ForeignKey("public_metrics.id", ondelete="SET NULL"), nullable=True)
    evidence_span = Column(Text, nullable=False)  # 생기부 텍스트 원문 발췌
    section_type = Column(String, nullable=True)
    evidence_type = Column(SQLEnum(EvidenceType), default=EvidenceType.MODEL, nullable=False)
    relevance_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    recommendation = relationship("Recommendation", back_populates="evidences")
    metric = relationship("PublicMetric")

class PublicMetric(Base):
    __tablename__ = "public_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String, nullable=False)  # KOSIS, 워크넷, 지역통계
    category = Column(String, nullable=False)  # 전공취업률, 직업전망, 지역수요
    key_name = Column(String, nullable=False, index=True)
    data = Column(JSON, nullable=False)
    reference_year = Column(Date, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    quality_flag = Column(SQLEnum(QualityFlag), default=QualityFlag.FRESH, nullable=False)

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recommendation_id = Column(UUID(as_uuid=True), ForeignKey("recommendations.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1 ~ 5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="feedbacks")
    recommendation = relationship("Recommendation", back_populates="feedbacks")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=False)
    metadata_info = Column(JSON, name="metadata", nullable=True)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")
