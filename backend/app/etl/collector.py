import httpx
from typing import Dict, Any, List
from app.core.logging import logger
from datetime import date

def fetch_kosis_major_employment() -> List[Dict[str, Any]]:
    """
    Mock query to Korean KOSIS OpenAPI endpoint.
    If actual endpoint keys were supplied, we would execute:
    response = httpx.get("http://kosis.kr/openapi/...", params=...)
    """
    logger.info("fetching_kosis_major_employment_data")
    try:
        # Mimic response
        return [
            {"major": "컴퓨터공학과", "employment_rate": 78.5, "year": 2025},
            {"major": "전자공학과", "employment_rate": 76.2, "year": 2025},
            {"major": "화학공학과", "employment_rate": 71.0, "year": 2025}
        ]
    except Exception as e:
        logger.error("kosis_fetch_error", error=str(e))
        return []

def fetch_worknet_job_forecast() -> List[Dict[str, Any]]:
    """
    Mock query to Worknet career forecasting REST API.
    """
    logger.info("fetching_worknet_job_forecast_data")
    try:
        return [
            {"job_title": "소프트웨어 엔지니어", "growth_index": "매우높음", "year": 2024},
            {"job_title": "데이터 과학자", "growth_index": "높음", "year": 2026}
        ]
    except Exception as e:
        logger.error("worknet_fetch_error", error=str(e))
        return []
