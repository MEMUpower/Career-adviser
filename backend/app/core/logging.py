import structlog
import sys
import logging
from sqlalchemy.orm import Session
from app.models.models import AuditLog
from typing import Optional, Dict, Any

# Configure structlog
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Standard Logging configuration
logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)

def log_audit(
    db: Session,
    action: str,
    resource_type: str,
    resource_id: str,
    user_id: Optional[str] = None,
    metadata_info: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
):
    """
    Log sensitive data access or modifications in the database for compliance and security audit.
    """
    try:
        audit_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            metadata_info=metadata_info or {},
            ip_address=ip_address
        )
        db.add(audit_entry)
        db.commit()
        
        # Also print to structured logs
        logger.info(
            "audit_log",
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            user_id=str(user_id) if user_id else "anonymous",
            ip_address=ip_address
        )
    except Exception as e:
        logger.error("failed_to_log_audit", error=str(e))
        db.rollback()
