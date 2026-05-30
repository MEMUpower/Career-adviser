from datetime import date, datetime

from app.config import settings
from app.core.logging import logger
from app.database import SessionLocal
from app.etl.collector import build_public_metric_sources
from app.models.models import PublicMetric, QualityFlag
from app.tasks.celery_app import celery_app


MOCK_PUBLIC_DATA_SOURCES = [
    {
        "source": "CareerNet",
        "category": "학과정보",
        "key_name": "컴퓨터공학과",
        "data": {"employment_rate": "예시", "salary": "예시", "summary": "CareerNet API key가 없을 때 표시되는 샘플 데이터입니다."},
        "reference_year": date.today(),
    },
]


def _build_sources():
    careernet_sources = build_public_metric_sources()
    if careernet_sources:
        logger.info("careernet_public_sources_loaded", count=len(careernet_sources))
        return careernet_sources

    logger.warning("careernet_public_sources_fallback_to_mock")
    return MOCK_PUBLIC_DATA_SOURCES


@celery_app.task
def run_public_metrics_etl():
    """
    ETL job to fetch, clean, categorize and load public statistics on careers and employment.
    Uses CareerNet OpenAPI when an API key is available, otherwise falls back to sample data.
    """
    db = SessionLocal()
    logger.info("public_metrics_etl_started")
    try:
        loaded_count = 0
        sources = _build_sources()

        for src in sources:
            ref_date = src.get("reference_year") or date.today()
            delta_days = (date.today() - ref_date).days

            if delta_days > 365:
                q_flag = QualityFlag.STALE
            elif not src.get("data"):
                q_flag = QualityFlag.MISSING
            else:
                q_flag = QualityFlag.FRESH

            metric = db.query(PublicMetric).filter(
                PublicMetric.source == src["source"],
                PublicMetric.key_name == src["key_name"],
            ).first()

            if metric:
                metric.category = src["category"]
                metric.data = src["data"]
                metric.reference_year = ref_date
                metric.quality_flag = q_flag
                metric.updated_at = datetime.utcnow()
            else:
                metric = PublicMetric(
                    source=src["source"],
                    category=src["category"],
                    key_name=src["key_name"],
                    data=src["data"],
                    reference_year=ref_date,
                    quality_flag=q_flag,
                )
                db.add(metric)
            loaded_count += 1

        db.commit()
        logger.info("public_metrics_etl_success", records_count=loaded_count)
        return True
    except Exception as e:
        logger.error("public_metrics_etl_failed", error=str(e))
        db.rollback()
        return False
    finally:
        db.close()
