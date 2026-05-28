import re

def anonymize_text(text: str) -> str:
    """
    Mask names, school names, student IDs, and phone numbers in the document.
    """
    if not text:
        return ""
    
    # 1. Phone numbers: 010-XXXX-XXXX
    text = re.sub(r'01\d-\d{3,4}-\d{4}', '[전화번호 마스킹]', text)
    
    # 2. Student identification (Grade, Class, Number)
    # e.g., 3학년 2반 15번 -> X학년 X반 XX번
    text = re.sub(r'\d+학년\s*\d+반\s*\d+번', '[학번 마스킹]', text)
    
    # 3. School names ending with 고등학교, 중학교, 초등학교
    # e.g., 서울고등학교 -> XX고등학교
    text = re.sub(r'([가-힣]{2,10})(고등학교|중학교|초등학교)', r'○○\2', text)
    
    # 4. Korean names (Usually 2-4 letters) in typical patterns
    # Warning: Regex names can sometimes mask common words, but for safety in records, we focus on name formats
    # For MVP, we mask names after common keywords like "학생", "교사" or isolated names.
    # Simple common pattern for student name masking:
    # "성명 : 홍길동" -> "성명 : 홍○동"
    def mask_name_match(match):
        name = match.group(1)
        if len(name) == 2:
            return name[0] + "○"
        elif len(name) == 3:
            return name[0] + "○" + name[2]
        else:
            return name[0] + "○○" + name[-1]

    text = re.sub(r'(?:성명|이름)\s*:\s*([가-힣]{2,4})', lambda m: f"성명 : {mask_name_match(m)}", text)
    
    # Also mask common email patterns
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[이메일 마스킹]', text)
    
    return text
