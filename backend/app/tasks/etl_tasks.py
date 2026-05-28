from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models.models import PublicMetric, QualityFlag
from datetime import datetime, date
from app.core.logging import logger

# Mocking data since no API keys are provided.
# We parse, clean and load it into PostgreSQL.
MOCK_PUBLIC_DATA_SOURCES = [
    {
        "source": "KOSIS",
        "category": "전공취업률",
        "key_name": "컴퓨터공학과",
        "data": {"employment_rate": 78.5, "graduates": 12500, "average_salary_kwr": 3600000},
        "reference_year": date(2025, 12, 31)
    },
    {
        "source": "KOSIS",
        "category": "전공취업률",
        "key_name": "전자공학과",
        "data": {"employment_rate": 76.2, "graduates": 11000, "average_salary_kwr": 3800000},
        "reference_year": date(2025, 12, 31)
    },
    {
        "source": "워크넷",
        "category": "직업전망",
        "key_name": "소프트웨어 엔지니어",
        "data": {"growth_index": "매우높음", "job_security": "높음", "annual_openings": 4500},
        "reference_year": date(2024, 6, 1)  # Stale data check trial
    },
    {
        "source": "워크넷",
        "category": "직업전망",
        "key_name": "데이터 과학자",
        "data": {"growth_index": "높음", "job_security": "보통", "annual_openings": 2100},
        "reference_year": date(2026, 1, 1)
    },
    {
        "source": "지역통계",
        "category": "지역수요",
        "key_name": "스마트팩토리 제어",
        "data": {"demand_region": "경상북도", "cluster_count": 45, "growth_percentage": 12.8},
        "reference_year": date(2023, 10, 10) # STALE limit check
    }
]

@celery_app.task
def run_public_metrics_etl():
    """
    ETL job to fetch, clean, categorize and load public statistics on careers and employment.
    Handles data aging (STALE detection) and sets appropriate quality flags.
    """
    db = SessionLocal()
    logger.info("public_metrics_etl_started")
    try:
        loaded_count = 0
        for src in MOCK_PUBLIC_DATA_SOURCES:
            # 1. Cleaning & Quality control
            ref_date = src["reference_year"]
            delta_days = (date.today() - ref_date).days
            
            # If data is older than 365 days, mark it STALE
            if delta_days > 365:
                q_flag = QualityFlag.STALE
            elif not src["data"]:
                q_flag = QualityFlag.MISSING
            else:
                q_flag = QualityFlag.FRESH

            # 2. Check if already exists, else update
            metric = db.query(PublicMetric).filter(
                PublicMetric.source == src["source"],
                PublicMetric.key_name == src["key_name"]
            ).first()

            if metric:
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
                    quality_flag=q_flag
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
