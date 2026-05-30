from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

import httpx

from app.config import settings
from app.core.logging import logger

CAREERNET_MAJOR_URL = f"{settings.CAREERNET_BASE_URL.rstrip('/')}/cnet/openapi/getOpenApi"
CAREERNET_JOB_URL = f"{settings.CAREERNET_BASE_URL.rstrip('/')}/cnet/openapi/getOpenApi"
CAREERNET_JOB_JSON_URL = f"{settings.CAREERNET_BASE_URL.rstrip('/')}/cnet/openapi/getOpenApi.json"


def _get_json(url: str, params: Dict[str, Any]) -> Dict[str, Any]:
    with httpx.Client(timeout=30.0) as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        return response.json()


def _extract_content_list(payload: Dict[str, Any], root_key: str) -> List[Dict[str, Any]]:
    container = payload.get(root_key)
    if isinstance(container, dict):
        content = container.get("content")
        if isinstance(content, list):
            return content
        if isinstance(content, dict):
            return [content]
    if isinstance(container, list):
        return container
    return []


def _first_content(payload: Dict[str, Any], root_key: str) -> Dict[str, Any]:
    items = _extract_content_list(payload, root_key)
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

    payload = _get_json(CAREERNET_MAJOR_URL, params)
    return _extract_content_list(payload, "dataSearch")


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

    payload = _get_json(CAREERNET_MAJOR_URL, params)
    return _first_content(payload, "dataSearch")


def fetch_careernet_job_list(search_job_nm: Optional[str] = None, search_theme_code: Optional[str] = None, search_aptd_codes: Optional[str] = None, search_job_cd: Optional[str] = None, page_index: int = 1) -> List[Dict[str, Any]]:
    """Fetch CareerNet job encyclopedia list entries."""
    if not settings.CAREERNET_API_KEY:
        logger.warning("careernet_api_key_missing_jobs")
        return []

    params: Dict[str, Any] = {
        "apiKey": settings.CAREERNET_API_KEY,
        "svcType": "api",
        "svcCode": "JOB",
        "contentType": "json",
        "gubun": "job_dic_list",
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

    payload = _get_json(CAREERNET_JOB_JSON_URL, params)
    # The JSON shape can vary slightly across endpoints; normalize common containers.
    jobs = _extract_content_list(payload, "jobs")
    if jobs:
        return jobs
    jobs = _extract_content_list(payload, "dataSearch")
    if jobs:
        return jobs
    return payload.get("list", []) if isinstance(payload.get("list"), list) else []


def fetch_careernet_job_detail(seq: str) -> Dict[str, Any]:
    """Fetch CareerNet job encyclopedia detail."""
    if not settings.CAREERNET_API_KEY:
        logger.warning("careernet_api_key_missing_job_detail")
        return {}

    params = {
        "apiKey": settings.CAREERNET_API_KEY,
        "svcType": "api",
        "svcCode": "JOB_VIEW",
        "contentType": "json",
        "seq": seq,
    }

    payload = _get_json(CAREERNET_JOB_JSON_URL, params)
    if isinstance(payload, dict):
        if "job" in payload and isinstance(payload["job"], dict):
            return payload["job"]
        if "baseInfo" in payload or "forecastList" in payload:
            return payload
        if "dataSearch" in payload:
            return _first_content(payload, "dataSearch")
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

            major_item = major_list[0]
            major_seq = str(major_item.get("majorSeq", "")).strip()
            detail = fetch_careernet_major_detail(major_seq) if major_seq else {}

            sources.append(
                {
                    "source": "CareerNet",
                    "category": "학과정보",
                    "key_name": major_name,
                    "data": {
                        "major_seq": major_seq,
                        "l_class": major_item.get("lClass"),
                        "m_class": major_item.get("mClass"),
                        "facil_name": major_item.get("facilName"),
                        "employment_rate": detail.get("employment") or detail.get("employmentRate"),
                        "salary": detail.get("salary") or detail.get("avgSalary"),
                        "summary": detail.get("summary") or detail.get("majorSummary"),
                        "related_jobs": detail.get("job") or detail.get("relJob"),
                        "related_qualifications": detail.get("qualifications") or detail.get("license"),
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
            job_seq = str(job_item.get("jobdicSeq") or job_item.get("seq") or job_item.get("job_cd") or "").strip()
            detail = fetch_careernet_job_detail(job_seq) if job_seq else {}

            sources.append(
                {
                    "source": "CareerNet",
                    "category": "직업백과",
                    "key_name": target["name"],
                    "data": {
                        "job_cd": job_seq,
                        "job_nm": job_item.get("jobNm") or job_item.get("job_nm"),
                        "top_nm": job_item.get("topNm") or job_item.get("top_nm"),
                        "aptit_name": job_item.get("aptitName") or job_item.get("aptit_name"),
                        "work": detail.get("workList") or job_item.get("work"),
                        "forecast": detail.get("forecastList"),
                        "wage": detail.get("wage") or job_item.get("wage"),
                        "related_jobs": detail.get("rel_job_nm") or job_item.get("rel_job_nm"),
                        "summary": (detail.get("baseInfo") or {}).get("summary") if isinstance(detail.get("baseInfo"), dict) else None,
                        "curriculum": (detail.get("jobReadyList") or {}).get("curriculum") if isinstance(detail.get("jobReadyList"), dict) else None,
                    },
                    "reference_year": date.today(),
                }
            )
        except Exception as e:
            logger.error("careernet_job_fetch_failed", job_name=target["name"], error=str(e))

    return sources
