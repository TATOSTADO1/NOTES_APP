from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from MODELS.user import User


def get_by_id(db: Session, user_id: UUID) -> User | None:
    return db.scalar(select(User).where(User.id_user == user_id))


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def get_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == username))


def add(db: Session, user: User) -> User:
    db.add(user)
    db.flush()
    return user


def delete(db: Session, user: User) -> None:
    db.delete(user)
