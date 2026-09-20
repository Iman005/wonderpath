"""AuthRepository — data access for User rows only."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.infrastructure.db.models import User


class AuthRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_google_sub(self, google_sub: str) -> User | None:
        stmt = select(User).where(User.google_sub == google_sub)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(func.lower(User.email) == email.strip().lower())
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_id(self, user_id: str) -> User | None:
        return self.db.get(User, user_id)

    def create_user(
        self,
        *,
        google_sub: str | None = None,
        email: str | None = None,
        display_name: str | None = None,
        password_hash: str | None = None,
    ) -> User:
        user = User(
            google_sub=google_sub,
            email=email,
            display_name=display_name,
            password_hash=password_hash,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def save(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
