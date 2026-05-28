from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models.models import Record, RecordStatus, ParsedSection, Profile, Recommendation, RecommendationEvidence, PublicMetric
from app.pipeline.parser import extract_text_from_pdf, segment_sections
from app.pipeline.tagger import analyze_student_competency
from app.pipeline.recommender import generate_career_recommendations
from app.core.logging import logger
from sqlalchemy.exc import IntegrityError, OperationalError
import os

@celery_app.task(bind=True, max_retries=3, soft_time_limit=180, time_limit=240)
def process_student_record(self, record_id: str):
    db = SessionLocal()
    try:
        # Prevent concurrent processing of the same record by row-level locking.
        record = (
            db.query(Record)
            .filter(Record.id == record_id)
            .with_for_update(nowait=True)
            .first()
        )
    except OperationalError:
        logger.warning("record_locked_skip_duplicate_worker", record_id=record_id)
        db.close()
        return True

    if not record:
        logger.error("record_not_found_in_worker", record_id=record_id)
        db.close()
        return False

    try:
        # 1. Update status to PARSING
        record.status = RecordStatus.PARSING
        db.commit()
        logger.info("parsing_started", record_id=record_id)

        # Extract text & segment
        pages = extract_text_from_pdf(record.stored_path)
        sections = segment_sections(pages)

        # Reprocessing safety: clear previously parsed sections before re-insert.
        db.query(ParsedSection).filter(ParsedSection.record_id == record.id).delete(synchronize_session=False)
        db.commit()

        # Save parsed sections
        parsed_sec_objects = []
        for sec in sections:
            db_sec = ParsedSection(
                record_id=record.id,
                section_type=sec["section_type"],
                content=sec["content"],
                metadata_info=sec["metadata"]
            )
            db.add(db_sec)
            parsed_sec_objects.append(db_sec)
        db.commit()

        # 2. Update status to TAGGING
        record.status = RecordStatus.TAGGING
        db.commit()
        logger.info("competency_tagging_started", record_id=record_id)

        competency_results = analyze_student_competency(sections)

        # Upsert profile for idempotent reprocessing.
        db_profile = db.query(Profile).filter(Profile.record_id == record.id).first()
        if db_profile:
            db_profile.competency_scores = competency_results["competency_scores"]
            db_profile.interest_tags = competency_results["interest_tags"]
            db_profile.overall_confidence = competency_results["overall_confidence"]
            # Clear previous recommendations/evidences before creating new ones.
            db.query(Recommendation).filter(Recommendation.profile_id == db_profile.id).delete(synchronize_session=False)
        else:
            db_profile = Profile(
                record_id=record.id,
                competency_scores=competency_results["competency_scores"],
                interest_tags=competency_results["interest_tags"],
                overall_confidence=competency_results["overall_confidence"]
            )
            db.add(db_profile)
        try:
            db.commit()
        except IntegrityError:
            # Another concurrent task might have inserted profile just before commit.
            db.rollback()
            db_profile = db.query(Profile).filter(Profile.record_id == record.id).first()
            if not db_profile:
                raise
            db_profile.competency_scores = competency_results["competency_scores"]
            db_profile.interest_tags = competency_results["interest_tags"]
            db_profile.overall_confidence = competency_results["overall_confidence"]
            db.query(Recommendation).filter(Recommendation.profile_id == db_profile.id).delete(synchronize_session=False)
            db.commit()

        # 3. Update status to RECOMMENDING
        record.status = RecordStatus.RECOMMENDING
        db.commit()
        logger.info("career_recommendation_started", record_id=record_id)

        # Fetch active public metrics to feed the prompt
        metrics = db.query(PublicMetric).all()
        metrics_list = []
        for m in metrics:
            metrics_list.append({
                "source": m.source,
                "category": m.category,
                "key_name": m.key_name,
                "data": m.data,
                "quality_flag": m.quality_flag.value
            })

        # Calculate & Generate
        rec_results = generate_career_recommendations(
            profile_data={
                "competency_scores": db_profile.competency_scores,
                "interest_tags": db_profile.interest_tags
            },
            raw_sections=sections,
            public_metrics_list=metrics_list
        )

        # Save recommendations and evidence
        for rec in rec_results.get("recommendations", []):
            db_rec = Recommendation(
                profile_id=db_profile.id,
                rec_type=rec["rec_type"],
                rank=rec["rank"],
                target_name=rec["target_name"],
                score=rec["score"],
                explanation=rec["explanation"],
                action_plan=rec["action_plan"],
                confidence=rec["confidence"],
                weight_snapshot=rec.get("weight_snapshot")
            )
            db.add(db_rec)
            db.commit()

            # Evidences mapping
            for ev in rec.get("evidences", []):
                # Search matching public metric if applicable
                metric_id = None
                matched_metric = db.query(PublicMetric).filter(
                    PublicMetric.key_name == rec["target_name"]
                ).first()
                if matched_metric:
                    metric_id = matched_metric.id

                db_ev = RecommendationEvidence(
                    recommendation_id=db_rec.id,
                    metric_id=metric_id,
                    evidence_span=ev["evidence_span"],
                    section_type=ev.get("section_type"),
                    evidence_type="MODEL",
                    relevance_score=ev.get("relevance_score", 1.0)
                )
                db.add(db_ev)
            db.commit()

        # Update status to COMPLETED
        record.status = RecordStatus.COMPLETED
        db.commit()
        logger.info("processing_completed", record_id=record_id)

    except Exception as e:
        logger.error("processing_failed", record_id=record_id, error=str(e))
        db.rollback()
        record.status = RecordStatus.FAILED
        record.error_detail = {"detail": str(e)}
        db.commit()
    finally:
        db.close()
