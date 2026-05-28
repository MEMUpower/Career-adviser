from app.pipeline.anonymizer import anonymize_text

def test_anonymize_name_and_school():
    # Test School masking
    text_school = "저는 서울고등학교를 다니며 정보과학 동아리 활동을 하였습니다."
    anonymized_school = anonymize_text(text_school)
    assert "서울고등학교" not in anonymized_school
    assert "○○고등학교" in anonymized_school

    # Test Name masking pattern
    text_name = "성명 : 홍길동 학생은 교실 온도조절 센서를 제작함."
    anonymized_name = anonymize_text(text_name)
    assert "홍길동" not in anonymized_name
    assert "홍○동" in anonymized_name

    # Test Email masking
    text_email = "문의사항은 student@naver.com 으로 보내주세요."
    anonymized_email = anonymize_text(text_email)
    assert "student@naver.com" not in anonymized_email
    assert "[이메일 마스킹]" in anonymized_email
