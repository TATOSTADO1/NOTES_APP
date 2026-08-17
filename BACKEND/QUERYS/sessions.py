from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from MODELS.session import AuthSession, RefreshToken


def get_by_id(db: Session, session_id: UUID) -> AuthSession | None:
    return db.get(AuthSession, session_id)


def get_refresh_token_by_hash(
    db: Session, token_hash: str, *, lock: bool = False
) -> RefreshToken | None:
    statement = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    if lock:
        statement = statement.with_for_update()
    return db.scalar(statement)


def add_session(db: Session, auth_session: AuthSession) -> AuthSession:
    db.add(auth_session)
    db.flush()
    return auth_session


def add_refresh_token(db: Session, token: RefreshToken) -> RefreshToken:
    db.add(token)
    db.flush()
    return token


def revoke_all_by_user(db: Session, user_id: UUID, revoked_at: datetime) -> None:
    db.execute(
        update(AuthSession)
        .where(AuthSession.id_user == user_id, AuthSession.revoked_at.is_(None))
        .values(revoked_at=revoked_at)
    )
