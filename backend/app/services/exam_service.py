from typing import List, Dict, Any, Optional
import random
from datetime import datetime
from sqlalchemy.orm.attributes import flag_modified
from app.dao.exam_dao import ExamDAO
from app.dao.binder_dao import BinderDAO
from app.dao.deck_dao import DeckDAO
from app.dao.flashcard_dao import FlashcardDAO
from app.dao.note_dao import NoteDAO
from app.dao.quiz_dao import QuizDAO
from app.dao.study_session_dao import StudySessionDAO
from app.models.binder import Binder
from app.models.deck import Deck
from app.models.flashcard import Flashcard
from app.models.note import Note
from app.models.quiz import Quiz, QuizQuestion
from app.models.exam import ExamSession
from app.models.study_session import StudySession
from app.middlewares.error_handler import ResourceNotFoundError, ForbiddenError

class ExamService:
    def __init__(
        self,
        exam_dao: ExamDAO,
        binder_dao: BinderDAO,
        deck_dao: DeckDAO,
        flashcard_dao: FlashcardDAO,
        note_dao: NoteDAO,
        quiz_dao: QuizDAO,
        study_session_dao: StudySessionDAO
    ):
        self._exam_dao = exam_dao
        self._binder_dao = binder_dao
        self._deck_dao = deck_dao
        self._flashcard_dao = flashcard_dao
        self._note_dao = note_dao
        self._quiz_dao = quiz_dao
        self._study_session_dao = study_session_dao

    def _get_all_binder_ids(self, binder_id: int) -> List[int]:
        ids = [binder_id]
        children = self._binder_dao.db.query(Binder.id).filter_by(parent_id=binder_id).all()
        for child in children:
            ids.extend(self._get_all_binder_ids(child[0]))
        return ids

    def start_exam(
        self,
        user_id: int,
        binder_id: int,
        duration_minutes: int = 30,
        include_flashcards: bool = True,
        include_qcm: bool = True,
        question_limit: int = 20
    ) -> ExamSession:
        # Vérification du classeur
        binder = self._binder_dao.get_by_id(binder_id)
        if not binder:
            raise ResourceNotFoundError("Classeur introuvable.")
        if binder.user_id != user_id:
            raise ForbiddenError("Accès interdit à ce classeur.")

        # Récupération récursive des sous-classeurs
        binder_ids = self._get_all_binder_ids(binder_id)

        # 1. Récupération des Flashcards
        flashcards = []
        if include_flashcards:
            decks = self._deck_dao.db.query(Deck).filter(Deck.binder_id.in_(binder_ids)).all()
            deck_ids = [d.id for d in decks]
            if deck_ids:
                flashcards = self._flashcard_dao.db.query(Flashcard).filter(Flashcard.deck_id.in_(deck_ids)).all()

        # 2. Récupération des QCMs (questions de quiz déjà générées pour ces notes)
        qcm_questions = []
        if include_qcm:
            notes = self._note_dao.db.query(Note).filter(Note.binder_id.in_(binder_ids)).all()
            note_ids = [n.id for n in notes]
            if note_ids:
                quizzes = self._quiz_dao.db.query(Quiz).filter(Quiz.note_id.in_(note_ids)).all()
                quiz_ids = [q.id for q in quizzes]
                if quiz_ids:
                    qcm_questions = self._quiz_dao.db.query(QuizQuestion).filter(QuizQuestion.quiz_id.in_(quiz_ids)).all()

        # 3. Assemblage & Mixage
        items = []
        for card in flashcards:
            items.append({
                "item_type": "flashcard",
                "item_id": card.id,
                "front": card.front,
                "back": card.back,
                "options": None,
                "user_answer": None,
                "is_correct": None
            })

        for q in qcm_questions:
            items.append({
                "item_type": "qcm",
                "item_id": q.id,
                "front": q.question_text,
                "back": None,
                "options": q.options,
                "user_answer": None,
                "is_correct": None
            })

        if not items:
            raise ForbiddenError(
                "Pas assez de ressources d'apprentissage. "
                "Créez des flashcards ou générez des QCM depuis vos notes dans ce classeur pour démarrer un examen."
            )

        random.shuffle(items)
        selected_items = items[:question_limit]

        for idx, item in enumerate(selected_items):
            item["id"] = idx + 1

        # Création de la session
        session = ExamSession(
            user_id=user_id,
            binder_id=binder_id,
            duration_seconds=duration_minutes * 60,
            items_snapshot=selected_items
        )
        return self._exam_dao.create(session)

    def get_exam_session(self, user_id: int, session_id: int) -> ExamSession:
        session = self._exam_dao.get_by_id(session_id)
        if not session:
            raise ResourceNotFoundError("Session d'examen introuvable.")
        if session.user_id != user_id:
            raise ForbiddenError("Accès interdit à cet examen.")
        return session

    def submit_answer(
        self,
        user_id: int,
        session_id: int,
        item_id: int,
        answer: Any
    ) -> Dict[str, Any]:
        session = self.get_exam_session(user_id, session_id)
        
        if session.completed_at is not None:
            raise ForbiddenError("Cet examen a déjà été finalisé.")

        items = list(session.items_snapshot)
        target_item = next((item for item in items if item["id"] == item_id), None)
        if not target_item:
            raise ResourceNotFoundError("Question introuvable dans cet examen.")

        is_correct = False
        if target_item["item_type"] == "qcm":
            correct_opt = next((opt for opt in target_item["options"] if opt.get("correct")), None)
            correct_opt_id = correct_opt["id"] if correct_opt else None
            is_correct = (str(answer).strip().lower() == str(correct_opt_id).strip().lower())
            target_item["user_answer"] = answer
            target_item["is_correct"] = is_correct
        elif target_item["item_type"] == "flashcard":
            is_correct = (answer is True or answer == "correct" or str(answer) == "5" or answer == 5)
            target_item["user_answer"] = "correct" if is_correct else "incorrect"
            target_item["is_correct"] = is_correct

        session.items_snapshot = items
        flag_modified(session, "items_snapshot")
        self._exam_dao.update(session)

        return {"is_correct": is_correct}

    def complete_exam(self, user_id: int, session_id: int) -> ExamSession:
        session = self.get_exam_session(user_id, session_id)
        
        if session.completed_at is not None:
            return session

        items = session.items_snapshot
        qcm_items = [item for item in items if item["item_type"] == "qcm"]
        fc_items = [item for item in items if item["item_type"] == "flashcard"]

        qcm_correct = sum(1 for item in qcm_items if item.get("is_correct") is True)
        fc_correct = sum(1 for item in fc_items if item.get("is_correct") is True)

        qcm_score = (qcm_correct / len(qcm_items)) * 100 if qcm_items else None
        fc_score = (fc_correct / len(fc_items)) * 100 if fc_items else None

        total_items = len(items)
        total_correct = sum(1 for item in items if item.get("is_correct") is True)
        score_pct = (total_correct / total_items) * 100 if total_items > 0 else 0.0

        # Calcul du temps écoulé
        time_taken = (datetime.utcnow() - session.started_at).total_seconds()
        time_taken_seconds = min(int(time_taken), session.duration_seconds)

        session.completed_at = datetime.utcnow()
        session.score_pct = score_pct
        session.qcm_score = qcm_score
        session.flashcard_score = fc_score
        session.time_taken_seconds = time_taken_seconds
        
        updated_session = self._exam_dao.update(session)

        # Enregistrement d'une session d'étude statistique pour les cartes flash révisées
        if fc_items:
            study_session = StudySession(
                user_id=user_id,
                module="flashcard",
                duration_seconds=time_taken_seconds,
                cards_reviewed=len(fc_items),
                cards_correct=fc_correct
            )
            self._study_session_dao.create(study_session)

        return updated_session
