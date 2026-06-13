from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.evaluation import Evaluation, EvaluationItem
from app.dao.base_dao import BaseDAO


class EvaluationDAO(BaseDAO[Evaluation]):
    def __init__(self, db: Session):
        super().__init__(Evaluation, db)

    def get_by_note(self, note_internal_id: int) -> List[Evaluation]:
        return (
            self.db.query(self.model)
            .filter_by(note_id=note_internal_id)
            .order_by(self.model.created_at.desc())
            .all()
        )

    def get_latest_by_content_hash(
        self, note_internal_id: int, user_id: int, content_hash: str
    ) -> Optional[Evaluation]:
        """Dernière évaluation générée pour ce contenu de note (cache : évite de
        rappeler l'IA tant que la note n'a pas changé)."""
        return (
            self.db.query(self.model)
            .filter_by(note_id=note_internal_id, user_id=user_id, content_hash=content_hash)
            .order_by(self.model.created_at.desc())
            .first()
        )

    def get_item(self, item_id: int) -> Optional[EvaluationItem]:
        return self.db.get(EvaluationItem, item_id)

    def save_item(self, item: EvaluationItem) -> EvaluationItem:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
