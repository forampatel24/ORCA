"""User repository - docs 12_API_APEC."""
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.database.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def create_user(self, db: Session, *, email: str, password_hash: str, name: str = None) -> User:
        db_obj = User(email=email, password_hash=password_hash, name=name)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

user_repo = UserRepository(User)
