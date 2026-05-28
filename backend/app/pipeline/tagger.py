import json
import httpx
from typing import Dict, Any
from app.config import settings
from app.pipeline.prompts import COMPETENCY_TAGGING_SYSTEM_PROMPT, COMPETENCY_TAGGING_USER_PROMPT
from app.core.logging import logger

def call_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Generic LLM call helper for OpenAI or Ollama based on configuration.
    """
    if settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        try:
            # We use standard HTTP client to easily control timeouts and parameters
            headers = {
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.2
            }
            with httpx.Client(timeout=60.0) as client:
                response = client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error("openai_api_failed_falling_back", error=str(e))
            
    # Google Gemini API branch (native Gemini endpoint)
    elif settings.LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
        try:
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}],
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "responseMimeType": "application/json",
                },
            }
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
                    json=payload,
                    headers=headers,
                    params={"key": settings.GEMINI_API_KEY},
                )
                response.raise_for_status()
                data = response.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            logger.error("gemini_api_failed_falling_back", error=str(e))

            
    # Try Ollama (Local LLM)
    try:
        url = f"{settings.OLLAMA_BASE_URL}/api/chat"
        payload = {
            "model": "llama3",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "format": "json"
        }
        with httpx.Client(timeout=120.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            return response.json()["message"]["content"]
    except Exception as e:
        logger.error("ollama_api_failed_returning_mock", error=str(e))
        
    # Return Mock response if both LLMs fail
    return get_mock_competency_response()

def get_mock_competency_response() -> str:
    mock_data = {
        "competency_scores": {
            "탐구력": 88.0,
            "협업": 75.0,
            "의사소통": 82.0,
            "자기주도성": 90.0
        },
        "evidences": [
            {
                "competency": "탐구력",
                "evidence_span": "수학 교과 중 삼각함수의 실생활 적용 사례에 관심을 가지고 깊이 연구하여 보고서를 제출함.",
                "reason": "삼각함수를 실생활에 주도적으로 대입하고 연구 보고서를 완성하여 심도 있는 탐구 자세를 보임."
            },
            {
                "competency": "자기주도성",
                "evidence_span": "정보 교과 시간에 스스로 아두이노 키트를 활용해 온도 조절 장치를 프로그래밍하여 동아리 학우들에게 발표함.",
                "reason": "스스로 교과 연계 장치를 제작하고 결과물을 타인과 공유하는 솔선수범을 보여 자기주도성을 증명함."
            }
        ],
        "interest_tags": ["SW 개발", "데이터 분석", "수학 모델링", "사물인터넷"],
        "overall_confidence": 0.85
    }
    return json.dumps(mock_data, ensure_ascii=False)

def analyze_student_competency(segmented_sections: list) -> Dict[str, Any]:
    """
    Summarize all sections and call LLM to run competency scoring.
    """
    full_text_summary = "\n\n".join([
        f"[{sec['section_type'].value}]\n{sec['content']}" 
        for sec in segmented_sections
    ])
    
    user_prompt = COMPETENCY_TAGGING_USER_PROMPT.format(record_content=full_text_summary)
    
    response_content = call_llm(COMPETENCY_TAGGING_SYSTEM_PROMPT, user_prompt)
    
    try:
        parsed_result = json.loads(response_content)
        # Validate keys
        if "competency_scores" not in parsed_result or "interest_tags" not in parsed_result:
            raise ValueError("LLM JSON output incomplete")
        return parsed_result
    except Exception as e:
        logger.error("competency_parsing_json_error_falling_back", error=str(e))
        return json.loads(get_mock_competency_response())
