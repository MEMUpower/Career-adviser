import json
from typing import Any, Dict

import httpx
from openai import OpenAI

from app.config import settings
from app.core.logging import logger
from app.pipeline.prompts import COMPETENCY_TAGGING_SYSTEM_PROMPT, COMPETENCY_TAGGING_USER_PROMPT


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """
    LLM call helper.

    Priority:
    1) NVIDIA NIM / OpenAI-compatible provider
    2) OpenAI (legacy support)
    3) Ollama
    4) Mock fallback
    """
    if settings.LLM_PROVIDER in {"nvidia_nim", "openai"}:
        api_key = settings.NVIDIA_API_KEY if settings.LLM_PROVIDER == "nvidia_nim" else settings.OPENAI_API_KEY
        base_url = settings.NVIDIA_NIM_BASE_URL if settings.LLM_PROVIDER == "nvidia_nim" else "https://api.openai.com/v1"
        model = settings.NVIDIA_NIM_MODEL if settings.LLM_PROVIDER == "nvidia_nim" else "gpt-4o-mini"

        if api_key:
            try:
                client = OpenAI(api_key=api_key, base_url=base_url)
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.2,
                )
                return response.choices[0].message.content or "{}"
            except Exception as e:
                logger.error(
                    "nim_or_openai_api_failed_falling_back",
                    error=str(e),
                    provider=settings.LLM_PROVIDER,
                    model=model,
                    base_url=base_url,
                )

    try:
        url = f"{settings.OLLAMA_BASE_URL}/api/chat"
        payload = {
            "model": "llama3",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "format": "json",
        }
        with httpx.Client(timeout=120.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            return response.json()["message"]["content"]
    except Exception as e:
        logger.error("ollama_api_failed_returning_mock", error=str(e))

    return get_mock_competency_response()


def get_mock_competency_response() -> str:
    mock_data = {
        "competency_scores": {
            "탐구력": 88.0,
            "협업": 75.0,
            "의사소통": 82.0,
            "자기주도성": 90.0,
        },
        "evidences": [
            {
                "competency": "탐구력",
                "evidence_span": "수학 과목과 프로젝트에서 스스로 가설을 세우고 검증하는 태도가 관찰됨",
                "reason": "탐구 과정에서 문제를 정의하고 근거를 수집하는 역량이 확인됨",
            },
            {
                "competency": "자기주도성",
                "evidence_span": "정보 과목 수행에서 스스로 역할을 분담하고 마감 기한을 지키며 결과물을 완성함",
                "reason": "과제 수행 전반에서 자기주도적으로 계획하고 실행하는 모습이 드러남",
            },
        ],
        "interest_tags": ["SW 개발", "데이터 분석", "수학 모델링", "사물인터넷"],
        "overall_confidence": 0.85,
    }
    return json.dumps(mock_data, ensure_ascii=False)


def analyze_student_competency(segmented_sections: list) -> Dict[str, Any]:
    """
    Summarize all sections and call LLM to run competency scoring.
    """
    full_text_summary = "\n\n".join(
        [f"[{sec['section_type'].value}]\n{sec['content']}" for sec in segmented_sections]
    )

    user_prompt = COMPETENCY_TAGGING_USER_PROMPT.format(record_content=full_text_summary)
    response_content = call_llm(COMPETENCY_TAGGING_SYSTEM_PROMPT, user_prompt)

    try:
        parsed_result = json.loads(response_content)
        if "competency_scores" not in parsed_result or "interest_tags" not in parsed_result:
            raise ValueError("LLM JSON output incomplete")
        return parsed_result
    except Exception as e:
        logger.error("competency_parsing_json_error_falling_back", error=str(e))
        return json.loads(get_mock_competency_response())
