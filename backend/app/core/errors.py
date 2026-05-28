from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime

class CareerAdvisorException(Exception):
    def __init__(self, status_code: int, code: str, detail: str):
        self.status_code = status_code
        self.code = code
        self.detail = detail

class AuthenticationError(CareerAdvisorException):
    def __init__(self, detail: str = "인증에 실패했습니다."):
        super().__init__(status_code=401, code="AUTH_FAILED", detail=detail)

class PermissionDeniedError(CareerAdvisorException):
    def __init__(self, detail: str = "권한이 없습니다."):
        super().__init__(status_code=403, code="PERMISSION_DENIED", detail=detail)

class EntityNotFoundError(CareerAdvisorException):
    def __init__(self, detail: str = "요청하신 리소스를 찾을 수 없습니다."):
        super().__init__(status_code=404, code="NOT_FOUND", detail=detail)

class InvalidFileFormatError(CareerAdvisorException):
    def __init__(self, detail: str = "지원하지 않는 파일 포맷입니다."):
        super().__init__(status_code=400, code="INVALID_FILE_FORMAT", detail=detail)

class DocumentParsingError(CareerAdvisorException):
    def __init__(self, detail: str = "문서 분석 중 오류가 발생했습니다."):
        super().__init__(status_code=500, code="PARSING_FAILED", detail=detail)

class HallucinationDetectedError(CareerAdvisorException):
    def __init__(self, detail: str = "AI 추천의 신뢰성 검증에 실패했습니다. (환각 탐지)"):
        super().__init__(status_code=500, code="HALLUCINATION_DETECTED", detail=detail)

async def career_advisor_error_handler(request: Request, exc: CareerAdvisorException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "code": exc.code,
            "detail": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )

async def general_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "code": "HTTP_ERROR",
            "detail": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )
