from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.dao.exam_dao import ExamDAO
from app.dao.binder_dao import BinderDAO
from app.dao.deck_dao import DeckDAO
from app.dao.flashcard_dao import FlashcardDAO
from app.dao.note_dao import NoteDAO
from app.dao.quiz_dao import QuizDAO
from app.dao.study_session_dao import StudySessionDAO
from app.services.exam_service import ExamService
from app.schemas.exam_schema import ExamStartRequest, ExamAnswerRequest, ExamResponse
from app.middlewares.auth_middleware import jwt_required_middleware

exam_bp = Blueprint("exam", __name__)

# Initialisation des DAOs
exam_dao = ExamDAO(db.session)
binder_dao = BinderDAO(db.session)
deck_dao = DeckDAO(db.session)
flashcard_dao = FlashcardDAO(db.session)
note_dao = NoteDAO(db.session)
quiz_dao = QuizDAO(db.session)
study_session_dao = StudySessionDAO(db.session)

# Initialisation du service
exam_service = ExamService(
    exam_dao=exam_dao,
    binder_dao=binder_dao,
    deck_dao=deck_dao,
    flashcard_dao=flashcard_dao,
    note_dao=note_dao,
    quiz_dao=quiz_dao,
    study_session_dao=study_session_dao
)

@exam_bp.route("/start", methods=["POST"])
@jwt_required_middleware
def start_exam():
    user_id = int(get_jwt_identity())
    data_dict = request.get_json() or {}
    
    req_data = ExamStartRequest.model_validate(data_dict)
    
    session = exam_service.start_exam(
        user_id=user_id,
        binder_id=req_data.binder_id,
        duration_minutes=req_data.duration_minutes,
        include_flashcards=req_data.include_flashcards,
        include_qcm=req_data.include_qcm,
        question_limit=req_data.question_limit
    )
    
    # Utilisation de model_dump() pour formater items_snapshot -> items
    return jsonify(ExamResponse.model_validate(session).model_dump()), 201

@exam_bp.route("/<int:session_id>", methods=["GET"])
@jwt_required_middleware
def get_exam_session(session_id):
    user_id = int(get_jwt_identity())
    
    session = exam_service.get_exam_session(user_id=user_id, session_id=session_id)
    
    return jsonify(ExamResponse.model_validate(session).model_dump()), 200

@exam_bp.route("/<int:session_id>/questions/<int:item_id>/answer", methods=["POST"])
@jwt_required_middleware
def submit_answer(session_id, item_id):
    user_id = int(get_jwt_identity())
    data_dict = request.get_json() or {}
    
    req_data = ExamAnswerRequest.model_validate(data_dict)
    
    result = exam_service.submit_answer(
        user_id=user_id,
        session_id=session_id,
        item_id=item_id,
        answer=req_data.answer
    )
    
    return jsonify(result), 200

@exam_bp.route("/<int:session_id>/complete", methods=["POST"])
@jwt_required_middleware
def complete_exam(session_id):
    user_id = int(get_jwt_identity())
    
    session = exam_service.complete_exam(user_id=user_id, session_id=session_id)
    
    return jsonify(ExamResponse.model_validate(session).model_dump()), 200
