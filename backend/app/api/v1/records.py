from fastapi import APIRouter, Depends, UploadFile, File, Request, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, Student, Record, RecordStatus
from app.schemas.schemas import RecordResponse
from app.core.errors import InvalidFileFormatError, EntityNotFoundError
from app.core.logging import log_audit
from app.tasks.document_tasks import process_student_record
import hashlib
import os
import uuid
from datetime import datetime, timedelta
from app.config import settings

router = APIRouter()
STALE_PROCESSING_MINUTES = 3

@router.post("/upload", response_model=RecordResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_record(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Validation
    if not file.filename.lower().endswith(".pdf"):
        raise InvalidFileFormatError("학교생활기록부는 PDF 포맷만 지원합니다.")
        
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise EntityNotFoundError("해당 사용자의 학생 프로필이 존재하지 않습니다.")

    # 2. File hashing to prevent duplication
    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()
    
    existing_record = db.query(Record).filter(Record.file_hash == file_hash).first()
    if existing_record:
        stale_cutoff = datetime.utcnow() - timedelta(minutes=STALE_PROCESSING_MINUTES)
        is_stale = existing_record.updated_at and existing_record.updated_at < stale_cutoff

        # If an older in-progress task got interrupted, force re-queue.
        if existing_record.status in {
            RecordStatus.PENDING,
            RecordStatus.PARSING,
            RecordStatus.TAGGING,
            RecordStatus.RECOMMENDING,
        } and is_stale:
            existing_record.status = RecordStatus.PENDING
            existing_record.error_detail = None
            db.commit()
            process_student_record.delay(str(existing_record.id))
            log_audit(
                db,
                "UPLOAD_DUPLICATE_FILE_STALE_RETRY",
                "Record",
                str(existing_record.id),
                user_id=str(current_user.id),
                ip_address=request.client.host,
            )
            return existing_record

        # If the same file previously failed, allow retry by re-queueing the same record.
        if existing_record.status == RecordStatus.FAILED:
            existing_record.status = RecordStatus.PENDING
            existing_record.error_detail = None
            db.commit()
            process_student_record.delay(str(existing_record.id))
            log_audit(
                db,
                "UPLOAD_DUPLICATE_FILE_RETRY",
                "Record",
                str(existing_record.id),
                user_id=str(current_user.id),
                ip_address=request.client.host,
            )
            return existing_record

        # If record is completed or processing, return existing record.
        log_audit(db, "UPLOAD_DUPLICATE_FILE", "Record", str(existing_record.id), user_id=str(current_user.id), ip_address=request.client.host)
        return existing_record

    # 3. Save File
    file_id = uuid.uuid4()
    stored_filename = f"{file_id}.pdf"
    stored_path = os.path.join(settings.UPLOAD_DIR, stored_filename)
    
    with open(stored_path, "wb") as f:
        f.write(content)

    # 4. Save metadata in Database
    record = Record(
        id=file_id,
        student_id=student.id,
        original_filename=file.filename,
        stored_path=stored_path,
        file_hash=file_hash,
        status=RecordStatus.PENDING
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    log_audit(db, "UPLOAD_DOCUMENT", "Record", str(record.id), user_id=str(current_user.id), ip_address=request.client.host)

    # 5. Trigger Background Celery Pipeline
    process_student_record.delay(str(record.id))

    return record

@router.get("/{record_id}", response_model=RecordResponse)
def get_record_status(
    record_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise EntityNotFoundError("요청하신 분석 기록을 찾을 수 없습니다.")
        
    # Security: Ensure only the student owner (or teacher) can view this record status
    student = db.query(Student).filter(Student.id == record.student_id).first()
    if current_user.role == "student" and student.user_id != current_user.id:
        raise EntityNotFoundError("해당 문서에 대한 접근 권한이 없습니다.")

    return record
