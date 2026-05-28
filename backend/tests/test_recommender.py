import pytest
from app.pipeline.recommender import validate_evidences_against_record, calculate_recommendation_scores
from app.core.errors import HallucinationDetectedError

def test_recommendation_score_calculation():
    competencies = {"탐구력": 90.0, "협업": 80.0, "의사소통": 70.0, "자기주도성": 85.0}
    weights = {"탐구력": 0.4, "협업": 0.2, "의사소통": 0.2, "자기주도성": 0.2, "취업률가중치": 0.15}
    modifiers = {"컴퓨터공학과": 80.0}
    
    scores = calculate_recommendation_scores(competencies, weights, modifiers)
    # Validate result is calculated and float/int type mapping exists
    assert "컴퓨터공학과" in scores
    assert scores["컴퓨터공학과"] > 80.0

def test_hallucination_prevention_success():
    raw_sections = [
        {"content": "수학 교과 중 삼각함수의 실생활 적용 사례에 관심을 가지고 깊이 연구함."}
    ]
    recs = [
        {
            "target_name": "컴퓨터공학과",
            "evidences": [
                {"evidence_span": "삼각함수의 실생활 적용 사례"}
            ]
        }
    ]
    # Should not raise exception
    validate_evidences_against_record(recs, raw_sections)

def test_hallucination_prevention_failure():
    raw_sections = [
        {"content": "수학 교과 중 삼각함수의 실생활 적용 사례에 관심을 가지고 깊이 연구함."}
    ]
    recs = [
        {
            "target_name": "컴퓨터공학과",
            "evidences": [
                {"evidence_span": "학생이 전국 정보 경시대회에서 대상을 수상함."} # Hallucinated evidence
            ]
        }
    ]
    with pytest.raises(HallucinationDetectedError):
        validate_evidences_against_record(recs, raw_sections)
