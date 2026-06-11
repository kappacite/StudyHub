from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import db, limiter
from app.dao.quiz_dao import QuizDAO
from app.dao.note_dao import NoteDAO
from app.dao.deck_dao import DeckDAO
from app.dao.flashcard_dao import FlashcardDAO
from app.services.quiz_service import QuizService
from app.services.ai_service import AIService
from app.schemas.quiz_schema import (
    QuizGenerateRequest,
    QuizAnswerRequest,
    QuizCreateFlashcardsRequest,
    QuizResponse,
    QuizQuestionResponse
)
from app.schemas.flashcard_schema import FlashcardResponse
from app.middlewares.auth_middleware import jwt_required_middleware

quizzes_bp = Blueprint("quizzes", __name__)

# Initialisation des DAOs
quiz_dao = QuizDAO(db.session)
note_dao = NoteDAO(db.session)
deck_dao = DeckDAO(db.session)
flashcard_dao = FlashcardDAO(db.session)

# Initialisation des Services
ai_service = AIService()
quiz_service = QuizService(
    quiz_dao=quiz_dao,
    note_dao=note_dao,
    deck_dao=deck_dao,
    flashcard_dao=flashcard_dao,
    ai_service=ai_service
)

@quizzes_bp.route("/generate", methods=["POST"])
@jwt_required_middleware
@limiter.limit("10 per hour")
def generate_quiz():
    user_id = int(get_jwt_identity())
    data_dict = request.get_json() or {}
    
    # Validation
    req_data = QuizGenerateRequest.model_validate(data_dict)
    
    quiz = quiz_service.generate_quiz(
        user_id=user_id,
        note_id=req_data.note_id,
        question_count=req_data.question_count
    )
    
    return jsonify(QuizResponse.model_validate(quiz).model_dump()), 201

@quizzes_bp.route("/note/<int:note_id>", methods=["GET"])
@jwt_required_middleware
def get_quizzes_by_note(note_id):
    user_id = int(get_jwt_identity())
    
    quizzes = quiz_service.get_quizzes_by_note(user_id=user_id, note_id=note_id)
    
    return jsonify([QuizResponse.model_validate(q).model_dump() for q in quizzes]), 200

@quizzes_bp.route("/<int:quiz_id>", methods=["GET"])
@jwt_required_middleware
def get_quiz(quiz_id):
    user_id = int(get_jwt_identity())
    
    quiz = quiz_service.get_quiz(user_id=user_id, quiz_id=quiz_id)
    
    return jsonify(QuizResponse.model_validate(quiz).model_dump()), 200

@quizzes_bp.route("/<int:quiz_id>/questions/<int:question_id>/answer", methods=["POST"])
@jwt_required_middleware
def answer_question(quiz_id, question_id):
    user_id = int(get_jwt_identity())
    data_dict = request.get_json() or {}
    
    # Validation
    req_data = QuizAnswerRequest.model_validate(data_dict)
    
    question = quiz_service.answer_question(
        user_id=user_id,
        quiz_id=quiz_id,
        question_id=question_id,
        answer_id=req_data.answer_id
    )
    
    return jsonify(QuizQuestionResponse.model_validate(question).model_dump()), 200

@quizzes_bp.route("/<int:quiz_id>/complete", methods=["POST"])
@jwt_required_middleware
def complete_quiz(quiz_id):
    user_id = int(get_jwt_identity())
    
    quiz = quiz_service.complete_quiz(user_id=user_id, quiz_id=quiz_id)
    
    return jsonify(QuizResponse.model_validate(quiz).model_dump()), 200

@quizzes_bp.route("/<int:quiz_id>/create-flashcards", methods=["POST"])
@jwt_required_middleware
def create_flashcards(quiz_id):
    user_id = int(get_jwt_identity())
    data_dict = request.get_json() or {}
    
    # Validation
    req_data = QuizCreateFlashcardsRequest.model_validate(data_dict)
    
    cards = quiz_service.create_flashcards_from_wrong_answers(
        user_id=user_id,
        quiz_id=quiz_id,
        question_ids=req_data.question_ids,
        deck_id=req_data.deck_id
    )
    
    return jsonify([FlashcardResponse.model_validate(c).model_dump() for c in cards]), 201
