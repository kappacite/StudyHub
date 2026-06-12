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
