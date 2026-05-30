from __future__ import annotations

from datetime import date
from typing import Any, Dict, Iterable, List, Optional

import httpx

from app.core.logging import logger
from app.config import settings

CAREERNET_JSON_BASE = f"{settings.CAREERNET_BASE_URL.rstrip('/')}/cnet/openapi"
CAREERNET_JOB_LIST_URL = f"{settings.CAREERNET_BASE_URL.rstrip('/')}/cnet/front/openapi/jobs.json"
CAREERNET_JOB_DETAIL_URL = f"{settings.CAREERNET_BASE_URL.rstrip('/')}/cnet/front/openapi/job.json"


def _get_json(url: str, params: Dict[str, Any]) -> Dict[str, Any]:
    with httpx.Client(timeout=30.0) as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        return response.json()


def _extract_list(payload: Dict[str, Any], root_key: str) -> List[Dict[str, Any]]:
    value = payload.get(root_key)
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        content = value.get("content")
        if isinstance(content, list):
            return content
        if isinstance(content, dict):
            return [content]
    return []


def _first_item(payload: Dict[str, Any], root_key: str) -> Dict[str, Any]:
    items = _extract_list(payload, root_key)
    return items[0] if items else {}


def fetch_careernet_major_list(search_title: Optional[str] = None, gubun: str = "대학교", per_page: int = 20) -> List[Dict[str, Any]]:
    """Fetch CareerNet major list entries from the official OpenAPI."""
    if not settings.CAREERNET_API_KEY:
        logger.warning("careernet_api_key_missing_majors")
        return []

    params: Dict[str, Any] = {
        "apiKey": settings.CAREERNET_API_KEY,
        "svcType": "api",
        "svcCode": "MAJOR",
        "contentType": "json",
        "gubun": gubun,
        "perPage": per_page,
    }
    if search_title:
        params["searchTitle"] = search_title

    payload = _get_json(CAREERNET_JSON_BASE, params)
    return _extract_list(payload, "dataSearch")


def fetch_careernet_major_detail(major_seq: str, gubun: str = "대학교") -> Dict[str, Any]:
    """Fetch CareerNet major detail from the official OpenAPI."""
    if not settings.CAREERNET_API_KEY:
        logger.warning("careernet_api_key_missing_major_detail")
        return {}

    params: Dict[str, Any] = {
        "apiKey": settings.CAREERNET_API_KEY,
        "svcType": "api",
        "svcCode": "MAJOR_VIEW",
        "contentType": "json",
        "gubun": gubun,
        "majorSeq": major_seq,
    }

    payload = _get_json(CAREERNET_JSON_BASE, params)
    return _first_item(payload, "dataSearch")


def fetch_careernet_job_list(search_job_nm: Optional[str] = None, search_theme_code: Optional[str] = None, search_aptd_codes: Optional[str] = None, search_job_cd: Optional[str] = None, page_index: int = 1) -> List[Dict[str, Any]]:
    """Fetch CareerNet job encyclopedia list entries."""
    if not settings.CAREERNET_API_KEY:
        logger.warning("careernet_api_key_missing_jobs")
        return []

    params: Dict[str, Any] = {
        "apiKey": settings.CAREERNET_API_KEY,
        "pageIndex": page_index,
    }
    if search_job_nm:
        params["searchJobNm"] = search_job_nm
    if search_theme_code:
        params["searchThemeCode"] = search_theme_code
    if search_aptd_codes:
        params["searchAptdCodes"] = search_aptd_codes
    if search_job_cd:
        params["searchJobCd"] = search_job_cd

    payload = _get_json(CAREERNET_JOB_LIST_URL, params)
    return payload.get("jobs", []) if isinstance(payload.get("jobs"), list) else []


def fetch_careernet_job_detail(seq: str) -> Dict[str, Any]:
    """Fetch CareerNet job encyclopedia detail."""
    if not settings.CAREERNET_API_KEY:
        logger.warning("careernet_api_key_missing_job_detail")
        return {}

    params = {
        "apiKey": settings.CAREERNET_API_KEY,
        "seq": seq,
    }

    payload = _get_json(CAREERNET_JOB_DETAIL_URL, params)
    if isinstance(payload, dict):
        if "job" in payload and isinstance(payload["job"], dict):
            return payload["job"]
        if "baseInfo" in payload or "forecastList" in payload:
            return payload
    return payload if isinstance(payload, dict) else {}


def build_public_metric_sources() -> List[Dict[str, Any]]:
    """
    Build public metric snapshots using CareerNet data.
    Fallback to empty list if the API key is missing or the API call fails.
    """
    if not settings.CAREERNET_API_KEY:
        return []

    sources: List[Dict[str, Any]] = []

    major_targets = ["컴퓨터공학과", "전자공학과", "데이터사이언스학과"]
    for major_name in major_targets:
        try:
            major_list = fetch_careernet_major_list(search_title=major_name)
            if not major_list:
                continue

            major_seq = str(major_list[0].get("majorSeq", "")).strip()
            detail = fetch_careernet_major_detail(major_seq) if major_seq else {}

            sources.append(
                {
                    "source": "CareerNet",
                    "category": "학과정보",
                    "key_name": major_name,
                    "data": {
                        "major_seq": major_seq,
                        "l_class": major_list[0].get("lClass"),
                        "m_class": major_list[0].get("mClass"),
                        "facil_name": major_list[0].get("facilName"),
                        "employment_rate": detail.get("employment"),
                        "salary": detail.get("salary"),
                        "summary": detail.get("summary"),
                        "related_jobs": detail.get("job"),
                        "related_qualifications": detail.get("qualifications"),
                    },
                    "reference_year": date.today(),
                }
            )
        except Exception as e:
            logger.error("careernet_major_fetch_failed", major_name=major_name, error=str(e))

    job_targets = [
        {"name": "소프트웨어개발자", "theme": "102421", "aptd": "104740"},
        {"name": "데이터분석가", "theme": "102421", "aptd": "104742"},
        {"name": "정보보안전문가", "theme": "102421", "aptd": "104740"},
    ]
    for target in job_targets:
        try:
            job_list = fetch_careernet_job_list(
                search_job_nm=target["name"],
                search_theme_code=target["theme"],
                search_aptd_codes=target["aptd"],
            )
            if not job_list:
                continue

            job_item = job_list[0]
            job_seq = str(job_item.get("job_cd") or job_item.get("seq") or "").strip()
            detail = fetch_careernet_job_detail(job_seq) if job_seq else {}

            sources.append(
                {
                    "source": "CareerNet",
                    "category": "직업백과",
                    "key_name": target["name"],
                    "data": {
                        "job_cd": job_seq,
                        "job_nm": job_item.get("job_nm"),
                        "top_nm": job_item.get("top_nm") or job_item.get("tob_nm"),
                        "aptit_name": job_item.get("aptit_name"),
                        "work": detail.get("workList") or job_item.get("work"),
                        "forecast": detail.get("forecastList"),
                        "wage": detail.get("wage") or job_item.get("wage"),
                        "related_jobs": detail.get("rel_job_nm") or job_item.get("rel_job_nm"),
                        "summary": detail.get("baseInfo", {}).get("summary") if isinstance(detail.get("baseInfo"), dict) else None,
                        "curriculum": detail.get("jobReadyList", {}).get("curriculum") if isinstance(detail.get("jobReadyList"), dict) else None,
                    },
                    "reference_year": date.today(),
                }
            )
        except Exception as e:
            logger.error("careernet_job_fetch_failed", job_name=target["name"], error=str(e))

    return sources
