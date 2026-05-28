from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models.models import Record, Student, Profile, Recommendation
from app.config import settings
from app.core.logging import logger
from jinja2 import Template
import os

HTML_REPORT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>교사용 학생 진로 추천 리포트</title>
    <style>
        body { font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif; padding: 40px; color: #333; }
        .header { border-bottom: 2px solid #2B6CB0; padding-bottom: 10px; margin-bottom: 30px; }
        .student-info { background: #F7FAFC; padding: 20px; border-radius: 8px; margin-bottom: 35px; border-left: 5px solid #2B6CB0; }
        .section-title { font-size: 20px; color: #2B6CB0; border-bottom: 1px solid #E2E8F0; padding-bottom: 5px; margin-top: 30px; }
        .competency-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        .competency-table th, .competency-table td { border: 1px solid #E2E8F0; padding: 12px; text-align: left; }
        .competency-table th { background: #EDF2F7; }
        .rec-card { background: #FFF; border: 1px solid #E2E8F0; padding: 20px; border-radius: 8px; margin-top: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        .rec-card h3 { margin-top: 0; color: #2D3748; }
        .badge { display: inline-block; background: #EBF8FF; color: #2B6CB0; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>학생 진로 설계 추천 리포트</h1>
        <p>발행일: {{ date_str }} | 학년부 지도교사 송부용</p>
    </div>

    <div class="student-info">
        <h3>학생 정보</h3>
        <p><strong>이름(비식별화):</strong> {{ student.masked_name }}</p>
        <p><strong>학년:</strong> {{ student.grade }} | <strong>학교유형:</strong> {{ student.school_type }} | <strong>지역:</strong> {{ student.region }}</p>
    </div>

    <h2 class="section-title">1. 핵심 종합 역량 평가</h2>
    <table class="competency-table">
        <thead>
            <tr>
                <th>역량 명칭</th>
                <th>점수 (100점 만점)</th>
                <th>의견</th>
            </tr>
        </thead>
        <tbody>
            {% for name, score in profile.competency_scores.items() %}
            <tr>
                <td><strong>{{ name }}</strong></td>
                <td>{{ score }}점</td>
                <td>
                    {% if score >= 85 %}우수 역량으로서 진로 탐구의 강력한 기반을 제공함.
                    {% elif score >= 70 %}보통 이상의 역량으로 지속적인 심화 탐구가 필요함.
                    {% else %}추가 세특 활동을 통한 보완이 권장됨.
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <h2 class="section-title">2. 추천 진로 시나리오 (Top 2)</h2>
    {% for rec in recommendations %}
    <div class="rec-card">
        <h3>
            <span class="badge">{{ rec.rec_type.value }}</span> {{ rec.target_name }}
        </h3>
        <p><strong>종합 적합도:</strong> {{ rec.score }}점 | <strong>추천 신뢰도:</strong> {{ (rec.confidence * 100) | round(1) }}%</p>
        <p><strong>교사 추천 의견:</strong> {{ rec.explanation }}</p>
        <p style="background: #FFF9E6; padding: 10px; border-radius: 4px;"><strong>주요 차기 액션플랜:</strong> {{ rec.action_plan }}</p>
    </div>
    {% endfor %}

    <div style="margin-top: 50px; font-size: 11px; color: #A0AEC0; text-align: center;">
        본 리포트는 AI 기반 학교생활기록부 정량 분석 및 교육 통계 데이터베이스를 근거로 작성되었으며 최종 진로 의사결정 시 참고용으로 활용해 주시기 바랍니다.
    </div>
</body>
</html>
"""

@celery_app.task
def generate_student_pdf_report(record_id: str) -> str:
    """
    Generate PDF Report from database data.
    Saves PDF file to reports folder and returns the file path.
    """
    from weasyprint import HTML
    
    db = SessionLocal()
    try:
        record = db.query(Record).filter(Record.id == record_id).first()
        if not record:
            return ""

        student = db.query(Student).filter(Student.id == record.student_id).first()
        profile = db.query(Profile).filter(Profile.record_id == record.id).first()
        
        if not student or not profile:
            return ""

        recommendations = db.query(Recommendation).filter(
            Recommendation.profile_id == profile.id
        ).order_by(Recommendation.rank.asc()).limit(2).all()

        # Render template
        template = Template(HTML_REPORT_TEMPLATE)
        rendered_html = template.render(
            student=student,
            profile=profile,
            recommendations=recommendations,
            date_str=date.today().strftime("%Y년 %m월 %d일")
        )

        output_filename = f"report_{record_id}.pdf"
        output_path = os.path.join(settings.REPORT_DIR, output_filename)

        # Generate PDF with WeasyPrint
        HTML(string=rendered_html).write_pdf(output_path)
        logger.info("pdf_report_generated", path=output_path)
        
        return output_path
    except Exception as e:
        logger.error("pdf_report_generation_failed", error=str(e), record_id=record_id)
        return ""
    finally:
        db.close()
