from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.dao.base_dao import BaseDAO

class UserDAO(BaseDAO[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(self.model).filter_by(email=email).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(self.model).filter_by(username=username).first()
