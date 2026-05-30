import json
import math
import re
from typing import Any, Dict, List

from app.core.errors import HallucinationDetectedError
from app.core.logging import logger
from app.pipeline.prompts import RECOMMENDATION_SYSTEM_PROMPT, RECOMMENDATION_USER_PROMPT
from app.pipeline.tagger import call_llm

DEFAULT_WEIGHTS = {
    "탐구력": 0.4,
    "협업": 0.2,
    "의사소통": 0.2,
    "자기주도성": 0.2,
    "취업률가중치": 0.15,
    "전망가중치": 0.10,
}

CAREERNET_MAJOR_TARGETS = {
    "컴퓨터공학과",
    "전자공학과",
    "화학공학과",
    "데이터사이언스학과",
}

CAREERNET_JOB_TARGETS = {
    "백엔드 개발자",
    "데이터 분석가",
    "정보보안전문가",
    "소프트웨어개발자",
}


def load_recommendation_mock_data() -> Dict[str, Any]:
    return {
        "recommendations": [
            {
                "rec_type": "major",
                "rank": 1,
                "target_name": "컴퓨터공학과",
                "score": 94.5,
                "explanation": "생기부에서 수학과 정보 관련 탐구 활동이 반복적으로 관찰되고, 문제 해결과 프로젝트 완성도가 높아 컴퓨터공학과와의 적합도가 높습니다. CareerNet 학과정보에서도 관련 분야의 진로 연결성이 강하게 나타납니다.",
                "action_plan": "1. 자료구조와 알고리즘 학습\n2. Python 프로젝트 제작\n3. 학교 동아리 또는 해커톤 참여",
                "confidence": 0.95,
                "evidences": [
                    {
                        "evidence_span": "수학 과목과 프로젝트에서 스스로 가설을 세우고 검증하는 태도가 관찰됨",
                        "section_type": "세특",
                        "relevance_score": 0.98,
                    }
                ],
            },
            {
                "rec_type": "job",
                "rank": 1,
                "target_name": "백엔드 개발자",
                "score": 93.0,
                "explanation": "프로젝트 완성도와 구현 역량이 높고, CareerNet 직업백과에서 요구하는 문제 해결형 업무와의 연결성이 좋습니다.",
                "action_plan": "1. REST API 설계 연습\n2. Git/GitHub 협업 습관화\n3. 간단한 웹 서비스 배포",
                "confidence": 0.96,
                "evidences": [
                    {
                        "evidence_span": "프로젝트 수행 시 요구사항 분석과 구현을 끝까지 완수함",
                        "section_type": "창체",
                        "relevance_score": 0.95,
                    }
                ],
            },
        ]
    }


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", "", text or "").lower()


def _is_major_target(name: str) -> bool:
    return name in CAREERNET_MAJOR_TARGETS or name.endswith("학과")


def _is_job_target(name: str) -> bool:
    return name in CAREERNET_JOB_TARGETS or name.endswith("개발자") or name.endswith("분석가") or name.endswith("전문가")


def _extract_metric_bonus(metric: Dict[str, Any]) -> float:
    data = metric.get("data") or {}
    quality_flag = (metric.get("quality_flag") or "FRESH").upper()
    freshness_multiplier = 1.0 if quality_flag == "FRESH" else 0.7 if quality_flag == "STALE" else 0.3

    bonus = 0.0
    employment_rate = data.get("employment_rate")
    if isinstance(employment_rate, (int, float)):
        bonus += max(0.0, min(float(employment_rate), 100.0)) * 0.18

    salary = data.get("salary") or data.get("average_salary_kwr")
    if isinstance(salary, (int, float)):
        bonus += min(float(salary) / 1000000.0, 10.0) * 0.4

    growth_index = data.get("growth_index")
    if isinstance(growth_index, str):
        growth_text = growth_index.lower()
        if any(token in growth_text for token in ["높", "상", "많", "우수", "good", "high"]):
            bonus += 8.0
        elif any(token in growth_text for token in ["보통", "medium", "normal"]):
            bonus += 4.0
        else:
            bonus += 2.0

    growth_percentage = data.get("growth_percentage")
    if isinstance(growth_percentage, (int, float)):
        bonus += min(float(growth_percentage), 30.0) * 0.3

    return round(bonus * freshness_multiplier, 2)


def _build_metric_lookup(public_metrics_list: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    lookup: Dict[str, List[Dict[str, Any]]] = {}
    for metric in public_metrics_list or []:
        key = str(metric.get("key_name") or "").strip()
        if not key:
            continue
        lookup.setdefault(key, []).append(metric)
    return lookup


def _career_metric_boost(target_name: str, public_metrics_list: List[Dict[str, Any]]) -> float:
    lookup = _build_metric_lookup(public_metrics_list)
    boosts: List[float] = []

    for metric in lookup.get(target_name, []):
        boosts.append(_extract_metric_bonus(metric))

    if boosts:
        return round(max(boosts), 2)

    # Gentle fallback: try fuzzy association by category.
    category_boosts: List[float] = []
    for metric in public_metrics_list or []:
        category = str(metric.get("category") or "")
        if _is_major_target(target_name) and "학과" in category:
            category_boosts.append(_extract_metric_bonus(metric) * 0.7)
        elif _is_job_target(target_name) and "직업" in category:
            category_boosts.append(_extract_metric_bonus(metric) * 0.7)

    return round(max(category_boosts), 2) if category_boosts else 0.0


def calculate_recommendation_scores(
    competency_scores: Dict[str, float],
    weights: Dict[str, float],
    public_metrics_list: List[Dict[str, Any]],
) -> Dict[str, float]:
    """
    Calculate candidate scores using competency signals plus CareerNet public metrics.
    """
    major_targets = ["컴퓨터공학과", "전자공학과", "화학공학과", "데이터사이언스학과"]
    job_targets = ["백엔드 개발자", "데이터 분석가", "정보보안전문가", "소프트웨어개발자"]

    base_scores = {
        "컴퓨터공학과": 80.0,
        "전자공학과": 75.0,
        "화학공학과": 72.0,
        "데이터사이언스학과": 78.0,
        "백엔드 개발자": 82.0,
        "데이터 분석가": 79.0,
        "정보보안전문가": 81.0,
        "소프트웨어개발자": 83.0,
    }

    comp_score = 0.0
    for key, weight in weights.items():
        if key in competency_scores and isinstance(competency_scores[key], (int, float)):
            comp_score += (float(competency_scores[key]) / 100.0) * float(weight)

    scores: Dict[str, float] = {}
    for target_name, base in base_scores.items():
        metric_boost = _career_metric_boost(target_name, public_metrics_list)
        if _is_major_target(target_name):
            metric_weight = float(weights.get("취업률가중치", 0.15))
        else:
            metric_weight = float(weights.get("전망가중치", 0.10))

        final_score = base + (comp_score * 20.0) + (metric_boost * metric_weight)
        scores[target_name] = round(final_score, 2)

    return scores


def validate_evidences_against_record(
    recommendations: List[Dict[str, Any]],
    raw_sections: List[Dict[str, Any]],
):
    full_original_text = " ".join([sec["content"] for sec in raw_sections]).strip()
    normalized_original = _normalize_text(full_original_text)

    for rec in recommendations:
        for ev in rec.get("evidences", []):
            span = ev.get("evidence_span", "").strip()
            if not span:
                continue

            normalized_span = _normalize_text(span)
            if normalized_span not in normalized_original:
                logger.error("hallucination_detected", evidence_span=span, recommendation=rec.get("target_name"))
                raise HallucinationDetectedError(
                    detail=f"추천 근거 문장('{span[:30]}...')이 생기부 원문과 일치하지 않습니다."
                )


def generate_career_recommendations(
    profile_data: Dict[str, Any],
    raw_sections: List[Dict[str, Any]],
    public_metrics_list: List[Dict[str, Any]],
    custom_weights: Dict[str, float] = None,
) -> Dict[str, Any]:
    """
    Generate recommendations from profile + raw text + CareerNet public metrics.
    """
    weights = custom_weights or DEFAULT_WEIGHTS
    metrics_str = json.dumps(public_metrics_list, ensure_ascii=False, indent=2)

    user_prompt = RECOMMENDATION_USER_PROMPT.format(
        competency_scores=json.dumps(profile_data.get("competency_scores", {}), ensure_ascii=False),
        interest_tags=json.dumps(profile_data.get("interest_tags", []), ensure_ascii=False),
        record_summary=" ".join([s["content"][:200] for s in raw_sections]),
        public_metrics=metrics_str,
    )

    response_content = call_llm(RECOMMENDATION_SYSTEM_PROMPT, user_prompt)

    try:
        parsed_result = json.loads(response_content)
        recs = parsed_result.get("recommendations", [])

        scores_map = calculate_recommendation_scores(
            competency_scores=profile_data.get("competency_scores", {}),
            weights=weights,
            public_metrics_list=public_metrics_list,
        )

        for rec in recs:
            target_name = rec.get("target_name")
            if target_name in scores_map:
                rec["score"] = scores_map[target_name]
            rec["weight_snapshot"] = weights

            if target_name:
                career_boost = _career_metric_boost(target_name, public_metrics_list)
                rec["career_metric_bonus"] = career_boost

        validate_evidences_against_record(recs, raw_sections)
        parsed_result["recommendations"] = recs
        return parsed_result
    except HallucinationDetectedError:
        raise
    except Exception as e:
        logger.error("recommendation_llm_failed_falling_back", error=str(e))
        return load_recommendation_mock_data()
