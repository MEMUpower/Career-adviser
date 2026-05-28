from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import get_current_user, RoleChecker
from app.models.models import User, UserRole, Record
from app.core.errors import EntityNotFoundError
from app.core.logging import log_audit
from app.tasks.report_tasks import generate_student_pdf_report
import uuid
import os

router = APIRouter()

# Restricted access to Teacher or Admin roles only
teacher_permission = RoleChecker(allowed_roles=[UserRole.TEACHER, UserRole.ADMIN])

@router.post("/generate/{record_id}", dependencies=[Depends(teacher_permission)])
def trigger_report_generation(
    request: Request,
    record_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise EntityNotFoundError("해당 생기부 파일을 찾을 수 없습니다.")

    # Call task synchronously (using delay is async, for MVP response we can wait or return path)
    # Since Weasyprint compiles PDF within a few seconds, we can run it and return the download URL
    task_res = generate_student_pdf_report.apply(args=[str(record_id)])
    pdf_path = task_res.get()
    
    if not pdf_path or not os.path.exists(pdf_path):
        raise EntityNotFoundError("PDF 리포트 생성에 실패했습니다.")

    log_audit(db, "GENERATE_PDF_REPORT", "Record", str(record_id), user_id=str(current_user.id), ip_address=request.client.host)
    
    return {
        "success": True,
        "message": "리포트가 생성되었습니다.",
        "download_url": f"/api/v1/reports/download/{record_id}"
    }

@router.get("/download/{record_id}", dependencies=[Depends(teacher_permission)])
def download_pdf_report(
    record_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    filename = f"report_{record_id}.pdf"
    from app.config import settings
    pdf_path = os.path.join(settings.REPORT_DIR, filename)

    if not os.path.exists(pdf_path):
        # Trigger generation dynamically if file is missing
        pdf_path = generate_student_pdf_report(str(record_id))
        if not pdf_path or not os.path.exists(pdf_path):
            raise EntityNotFoundError("요청하신 리포트 파일이 서버에 존재하지 않습니다.")

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"student_report_{record_id[:8]}.pdf"
    )
