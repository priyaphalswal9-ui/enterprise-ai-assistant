from sqlalchemy.orm import Session

from backend.app.core.security import hash_password, verify_password
from backend.app.models.user import User
from backend.app.schemas.auth import LoginRequest, RegisterRequest


def register_user(db: Session, data: RegisterRequest) -> User:
    existing_user = db.query(User).filter(User.email == data.email).first()

    if existing_user:
        raise ValueError("Email already registered")

    hashed_password = hash_password(data.password)

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hashed_password,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(db: Session, data: LoginRequest) -> User:
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise ValueError("Invalid email or password")

    if not verify_password(data.password, user.password_hash):
        raise ValueError("Invalid email or password")

    return user


def change_password(
    db: Session,
    user_id: int,
    current_password: str,
    new_password: str,
) -> None:
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise ValueError("User not found")

    if not verify_password(current_password, user.password_hash):
        raise ValueError("Current password is incorrect")

    user.password_hash = hash_password(new_password)

    db.commit()