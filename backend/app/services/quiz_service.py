from typing import List, Optional
from datetime import datetime
from app.dao.quiz_dao import QuizDAO
from app.dao.note_dao import NoteDAO
from app.dao.deck_dao import DeckDAO
from app.dao.flashcard_dao import FlashcardDAO
from app.models.quiz import Quiz, QuizQuestion
from app.models.flashcard import Flashcard
from app.services.ai_service import AIService
from app.middlewares.error_handler import ResourceNotFoundError, ForbiddenError

class QuizService:
    def __init__(
        self,
        quiz_dao: QuizDAO,
        note_dao: NoteDAO,
        deck_dao: DeckDAO,
        flashcard_dao: FlashcardDAO,
        ai_service: AIService
    ):
        self._quiz_dao = quiz_dao
        self._note_dao = note_dao
        self._deck_dao = deck_dao
        self._flashcard_dao = flashcard_dao
        self._ai_service = ai_service

    def generate_quiz(self, user_id: int, note_id: int, question_count: int = 7) -> Quiz:
        # Vérification de la note (propriétaire OU note partagée accessible).
        note = self._note_dao.get_by_id(note_id)
        if not note:
            raise ResourceNotFoundError("Note introuvable.")
        from app.utils.security import check_note_access
        check_note_access(self._note_dao.db, note, user_id)

        # Appel au service d'IA
        raw_questions = self._ai_service.generate_quiz(note.content, count=question_count)

        # Création du Quiz
        quiz = Quiz(note_id=note._id, user_id=user_id)
        created_quiz = self._quiz_dao.create(quiz)

        # Création des questions associées
        for q_data in raw_questions:
            q = QuizQuestion(
                quiz_id=created_quiz.id,
                question_text=q_data["question"],
                options=q_data["options"]
            )
            self._quiz_dao.save_question(q)

        # Re-fetch pour s'assurer que les relations sont chargées
        return self._quiz_dao.get_by_id(created_quiz.id)

    def get_quiz(self, user_id: int, quiz_id: int) -> Quiz:
        quiz = self._quiz_dao.get_by_id(quiz_id)
        if not quiz:
            raise ResourceNotFoundError("Quiz introuvable.")
        if quiz.user_id != user_id:
            raise ForbiddenError("Accès interdit à ce quiz.")
        return quiz

    def get_quizzes_by_note(self, user_id: int, note_id: int) -> List[Quiz]:
        # Vérification de la note (propriétaire OU note partagée accessible).
        note = self._note_dao.get_by_id(note_id)
        if not note:
            raise ResourceNotFoundError("Note introuvable.")
        from app.utils.security import check_note_access
        check_note_access(self._note_dao.db, note, user_id)

        # Isolation : ne renvoyer que les quiz de l'utilisateur (notes partagées).
        return self._quiz_dao.get_by_note_and_user(note._id, user_id)

    def answer_question(self, user_id: int, quiz_id: int, question_id: int, answer_id: str) -> QuizQuestion:
        # Vérification du quiz
        quiz = self.get_quiz(user_id, quiz_id)

        # Vérification de la question
        question = self._quiz_dao.get_question(question_id)
        if not question or question.quiz_id != quiz_id:
            raise ResourceNotFoundError("Question introuvable dans ce quiz.")

        # Vérifier que le quiz n'est pas déjà complété
        if quiz.completed_at is not None:
            raise ForbiddenError("Ce quiz a déjà été complété. Les réponses ne peuvent plus être modifiées.")

        # Validation de l'answer_id
        valid_option_ids = [opt["id"] for opt in question.options]
        if answer_id not in valid_option_ids:
            raise ForbiddenError(f"Option de réponse '{answer_id}' invalide pour cette question.")

        question.user_answer_id = answer_id
        return self._quiz_dao.save_question(question)

    def complete_quiz(self, user_id: int, quiz_id: int) -> Quiz:
        # Vérification du quiz
        quiz = self.get_quiz(user_id, quiz_id)

        if quiz.completed_at is not None:
            return quiz

        # Calcul du score
        correct_count = 0
        total_questions = len(quiz.questions)

        for q in quiz.questions:
            correct_option_id = next((opt["id"] for opt in q.options if opt.get("correct")), None)
            if q.user_answer_id == correct_option_id:
                correct_count += 1

        score_pct = (correct_count / total_questions) * 100 if total_questions > 0 else 0.0
        
        quiz.score_pct = score_pct
        quiz.completed_at = datetime.utcnow()

        return self._quiz_dao.update(quiz)

    def create_flashcards_from_wrong_answers(
        self,
        user_id: int,
        quiz_id: int,
        question_ids: List[int],
        deck_id: int
    ) -> List[Flashcard]:
        # Vérification du deck
        deck = self._deck_dao.get_by_id(deck_id)
        if not deck:
            raise ResourceNotFoundError("Deck introuvable.")
        if deck.user_id != user_id:
            raise ForbiddenError("Accès interdit à ce deck.")

        # Vérification du quiz
        quiz = self.get_quiz(user_id, quiz_id)
        if quiz.completed_at is None:
            raise ForbiddenError("Le quiz doit être complété avant de générer des flashcards à partir des mauvaises réponses.")

        created_cards = []
        for q_id in question_ids:
            # Recherche de la question correspondante dans ce quiz
            question = next((q for q in quiz.questions if q.id == q_id), None)
            if not question:
                continue

            # Vérifier si la réponse était fausse
            correct_option = next((opt for opt in question.options if opt.get("correct")), None)
            correct_option_id = correct_option["id"] if correct_option else None
            
            if question.user_answer_id != correct_option_id:
                correct_text = correct_option["text"] if correct_option else ""
                
                # Formatage du dos de la flashcard
                back_content = f"Réponse correcte : {correct_text}"
                
                card = Flashcard(
                    deck_id=deck_id,
                    front=question.question_text,
                    back=back_content
                )
                created_card = self._flashcard_dao.create(card)
                created_cards.append(created_card)

        return created_cards
