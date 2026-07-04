from sqlalchemy.orm import Session

from app.auth.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.users.models import User
from app.users.repository import UserRepository
from app.users.schemas import UserCreate, UserLogin


class UserService:

    @staticmethod
    def register(
        db: Session,
        payload: UserCreate,
    ) -> User:

        existing = UserRepository.get_by_email(
            db,
            payload.email,
        )

        if existing:
            raise ValueError("Email already registered.")

        user = User(
            full_name=payload.full_name,
            email=payload.email,
            password_hash=hash_password(payload.password),
        )

        return UserRepository.create(
            db,
            user,
        )

    @staticmethod
    def login(
        db: Session,
        payload: UserLogin,
    ) -> dict:

        user = UserRepository.get_by_email(
            db,
            payload.email,
        )

        if not user:
            raise ValueError("Invalid email or password.")

        if not verify_password(
            payload.password,
            user.password_hash,
        ):
            raise ValueError("Invalid email or password.")

        token = create_access_token(
            subject=str(user.id),
        )

        return {
            "access_token": token,
            "token_type": "bearer",
        }