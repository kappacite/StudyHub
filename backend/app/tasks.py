from app.extensions import celery_app, db
from app.dao.note_dao import NoteDAO
from app.dao.deck_dao import DeckDAO
from app.dao.flashcard_dao import FlashcardDAO
from app.dao.study_session_dao import StudySessionDAO
from app.services.ai_service import AIService
from app.services.stats_service import StatsService
from app.schemas.stats_schema import StudySessionCreate
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def run_blurting_analysis(self, user_id: int, note_id: int, user_blurting: str, duration_seconds: int) -> dict:
    """
    Asynchronously executes the blurting analysis using Gemini, saves the study session if applicable,
    and updates the note's last blurting timestamp.
    """
    logger.info(f"Starting async blurting analysis for user_id={user_id}, note_id={note_id}")
    try:
        note_dao = NoteDAO(db.session)
        note = note_dao.get_by_id(note_id)
        if not note:
            logger.error(f"Note {note_id} not found")
            raise ValueError("Note introuvable")
        if note.user_id != user_id:
            logger.error(f"User {user_id} does not own note {note_id}")
            raise ValueError("Accès interdit à cette note")

        ai_service = AIService()
        analysis_result = ai_service.analyze_blurting(note.title, note.content, user_blurting)

        # Enregistrement de la session d'étude si la durée est valide
        if duration_seconds > 0:
            deck_dao = DeckDAO(db.session)
            flashcard_dao = FlashcardDAO(db.session)
            study_session_dao = StudySessionDAO(db.session)
            stats_service = StatsService(study_session_dao, deck_dao, flashcard_dao)
            
            session_data = StudySessionCreate(
                module="note",
                duration_seconds=duration_seconds,
                cards_reviewed=0,
                cards_correct=0
            )
            stats_service.create_session(user_id, session_data)

        # Enregistrer la date du blurting
        note.last_blurting_at = datetime.utcnow()
        note_dao.update(note)
        
        # S'assurer que les modifications sont persistées
        db.session.commit()
        
        logger.info(f"Finished async blurting analysis for user_id={user_id}, note_id={note_id}")
        return analysis_result
    except Exception as e:
        db.session.rollback()
        logger.exception(f"Error executing blurting analysis task: {e}")
        raise


@celery_app.task(bind=True)
def run_class_gap_analysis(self, class_id: int) -> dict:
    """Calcule les lacunes d'une classe (data) + résumé IA optionnel, et met en cache.

    L'agrégation est synchrone et bornée ; seul le résumé IA (lent) justifie Celery.
    Tombe sur un résumé heuristique si l'IA est indisponible.
    """
    logger.info(f"Starting class gap analysis for class_id={class_id}")
    try:
        from app.dao.group_dao import GroupDAO
        from app.services.analytics_service import AnalyticsService
        from app.models.class_insight import ClassInsight

        analytics = AnalyticsService(GroupDAO(db.session))
        weak_topics = analytics.compute_weak_topics(class_id)
        weak_dicts = [t.model_dump() for t in weak_topics]

        ai_service = AIService()
        ai_summary = ai_service.summarize_class_gaps(weak_dicts)
        summary = ai_summary or AnalyticsService.heuristic_summary(weak_topics)

        payload = {"weak_topics": weak_dicts, "summary": summary, "ai": bool(ai_summary)}
        db.session.add(ClassInsight(group_id=class_id, payload=payload))
        db.session.commit()

        logger.info(f"Finished class gap analysis for class_id={class_id}")
        return payload
    except Exception as e:
        db.session.rollback()
        logger.exception(f"Error executing class gap analysis task: {e}")
        raise


@celery_app.task(bind=True)
def run_evaluation_generation(
    self, user_id: int, note_id, item_count: int = 8, force: bool = False
) -> dict:
    """Génère (ou réutilise via cache) une feuille d'évaluation pour une note.
    Asynchrone car l'appel Gemini est lent — calqué sur run_blurting_analysis."""
    logger.info(f"Starting async evaluation generation for user_id={user_id}, note_id={note_id}")
    try:
        from app.dao.evaluation_dao import EvaluationDAO
        from app.services.evaluation_service import EvaluationService

        note_dao = NoteDAO(db.session)
        evaluation_dao = EvaluationDAO(db.session)
        ai_service = AIService()
        service = EvaluationService(evaluation_dao, note_dao, ai_service)

        response = service.generate_evaluation(
            user_id=user_id, note_id=note_id, item_count=item_count, force=force
        )
        db.session.commit()

        logger.info(f"Finished async evaluation generation for user_id={user_id}, note_id={note_id}")
        return response.model_dump(mode="json")
    except Exception as e:
        db.session.rollback()
        logger.exception(f"Error executing evaluation generation task: {e}")
        raise
