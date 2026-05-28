import os
import re
from typing import Any, Dict, List

import pdfplumber
import pypdfium2 as pdfium
import pytesseract

from app.core.errors import DocumentParsingError
from app.core.logging import logger
from app.models.models import SectionType
from app.pipeline.anonymizer import anonymize_text

# Section identifier mapping to SectionType enum
SECTION_MARKERS = {
    SectionType.AWARDS: [r"수상경력", r"수상\s*경력"],
    SectionType.CREATIVE: [r"창의\s*체험활동", r"창체", r"동아리활동", r"봉사활동", r"자치활동"],
    SectionType.CAREER: [r"진로활동\s*상황", r"진로활동", r"진로\s*지도"],
    SectionType.SUBJECT: [r"교과학습\s*발달상황", r"교과\s*학습", r"내신성적"],
    SectionType.SETEUK: [r"세부능력\s*및\s*특기사항", r"세특", r"과목별\s*세특"],
    SectionType.READING: [r"독서활동\s*상황", r"독서\s*활동", r"독서활동"],
}


def _extract_text_with_pdfplumber(pdf_path: str) -> List[Dict[str, Any]]:
    pages_data: List[Dict[str, Any]] = []
    with pdfplumber.open(pdf_path) as pdf:
        for idx, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text and text.strip():
                pages_data.append({"page_number": idx + 1, "text": text})
    return pages_data


def _extract_text_with_ocr(pdf_path: str) -> List[Dict[str, Any]]:
    pages_data: List[Dict[str, Any]] = []
    doc = pdfium.PdfDocument(pdf_path)
    try:
        for idx in range(len(doc)):
            page = doc[idx]
            # Keep OCR bounded so a single problematic page cannot block the whole pipeline.
            pil_image = page.render(scale=1.5).to_pil()
            try:
                text = pytesseract.image_to_string(
                    pil_image,
                    lang="kor+eng",
                    timeout=20,
                )
            except RuntimeError as e:
                logger.warning("ocr_page_timeout", page_number=idx + 1, error=str(e))
                text = ""
            if text and text.strip():
                pages_data.append({"page_number": idx + 1, "text": text})
    finally:
        doc.close()
    return pages_data


def extract_text_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extract text per page from a PDF file.
    1) native text extraction (pdfplumber)
    2) OCR fallback (tesseract) for scanned/image PDFs
    """
    if not os.path.exists(pdf_path):
        raise DocumentParsingError("파일을 찾을 수 없습니다.")

    try:
        pages_data = _extract_text_with_pdfplumber(pdf_path)
        if pages_data:
            return pages_data

        logger.warning("native_text_empty_trying_ocr", path=pdf_path)
        ocr_pages = _extract_text_with_ocr(pdf_path)
        if ocr_pages:
            logger.info("ocr_fallback_succeeded", path=pdf_path, pages=len(ocr_pages))
            return ocr_pages

        raise DocumentParsingError(
            "PDF에서 텍스트를 추출할 수 없습니다. 이미지 기반 PDF라면 OCR 가능한 해상도(권장 200dpi 이상)로 다시 업로드해 주세요."
        )
    except DocumentParsingError:
        raise
    except Exception as e:
        logger.error("pdf_extraction_failed", error=str(e), path=pdf_path)
        raise DocumentParsingError(f"PDF 파싱 실패: {str(e)}")


def segment_sections(pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Segment full text into sections using regex markers.
    """
    segmented_data = []
    sections_text: Dict[SectionType, List[str]] = {st: [] for st in SectionType}
    current_section = SectionType.SUBJECT

    for page in pages_data:
        lines = page["text"].split("\n")
        for line in lines:
            matched = False
            for sec_type, patterns in SECTION_MARKERS.items():
                for pattern in patterns:
                    if re.search(pattern, line):
                        current_section = sec_type
                        matched = True
                        break
                if matched:
                    break

            anonymized_line = anonymize_text(line)
            sections_text[current_section].append(anonymized_line)

    for sec_type, lines in sections_text.items():
        if lines:
            content = "\n".join(lines).strip()
            if content:
                segmented_data.append(
                    {
                        "section_type": sec_type,
                        "content": content,
                        "metadata": {"length": len(content)},
                    }
                )

    if not segmented_data:
        raise DocumentParsingError(
            "추출된 생기부 섹션이 없습니다. 생활기록부 규격과 일치하는지 확인해 주세요."
        )

    return segmented_data
