from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1 import auth, records, recommendations, reports
from app.core.errors import (
    CareerAdvisorException, 
    career_advisor_error_handler, 
    general_http_exception_handler
)
from app.database import engine, Base
from app.core.logging import logger
import uvicorn

# Initialize database tables automatically for smooth local execution setup
try:
    Base.metadata.create_all(bind=engine)
    logger.info("database_tables_initialized_successfully")
except Exception as e:
    logger.error("database_table_initialization_failed", error=str(e))

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="생기부 업로드 기반 + 공공데이터 연계 진로 추천 웹서비스 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Set CORS Origins to support local frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(CareerAdvisorException, career_advisor_error_handler)
app.add_exception_handler(HTTPException, general_http_exception_handler)

# Include Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(records.router, prefix=f"{settings.API_V1_STR}/records", tags=["Student Records"])
app.include_router(recommendations.router, prefix=f"{settings.API_V1_STR}/recommendations", tags=["Career Recommendations"])
app.include_router(reports.router, prefix=f"{settings.API_V1_STR}/reports", tags=["Teacher Reports"])

@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
