from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session

T = TypeVar("T")

class BaseDAO(Generic[T]):
    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, entity_id: int) -> Optional[T]:
        return self.db.get(self.model, entity_id)

    def get_all(self, user_id: int, limit: int = 20, offset: int = 0) -> List[T]:
        return (
            self.db.query(self.model)
            .filter_by(user_id=user_id)
            .limit(limit)
            .offset(offset)
            .all()
        )

    def create(self, entity: T) -> T:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def update(self, entity: T) -> T:
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, entity: T) -> None:
        self.db.delete(entity)
        self.db.commit()
