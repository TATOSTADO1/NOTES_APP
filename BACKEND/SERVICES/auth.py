from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from CORE.config import settings
from CORE.encryption import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from MODELS.session import AuthSession, RefreshToken
from MODELS.user import User
from QUERYS import sessions as session_queries
from QUERYS import users as user_queries
from SCHEMAS.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from SERVICES.errors import ServiceError


def _as_utc(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def is_session_expired(auth_session: AuthSession, now: datetime) -> bool:
    inactive_since = now - timedelta(days=settings.REFRESH_TOKEN_INACTIVITY_DAYS)
    return (
        _as_utc(auth_session.expires_at) <= now
        or _as_utc(auth_session.last_used_at) <= inactive_since
    )


def _issue_refresh_token(db: Session, auth_session: AuthSession) -> tuple[str, RefreshToken]:
    raw_token = create_refresh_token()
    token = RefreshToken(
        id_session=auth_session.id_session,
        token_hash=hash_refresh_token(raw_token),
    )
    session_queries.add_refresh_token(db, token)
    return raw_token, token


def _create_session(
    db: Session, user: User, device_name: str | None
) -> TokenResponse:
    now = datetime.now(timezone.utc)
    auth_session = AuthSession(
        id_user=user.id_user,
        device_name=device_name.strip() if device_name else None,
        last_used_at=now,
        expires_at=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    session_queries.add_session(db, auth_session)
    refresh_token, _ = _issue_refresh_token(db, auth_session)
    return TokenResponse(
        access_token=create_access_token(user.id_user, auth_session.id_session),
        refresh_token=refresh_token,
    )


def register_user(db: Session, data: RegisterRequest) -> TokenResponse:
    if user_queries.get_by_email(db, str(data.email)):
        raise ServiceError(409, "El correo ya está registrado")
    if user_queries.get_by_username(db, data.username):
        raise ServiceError(409, "El nombre de usuario ya está registrado")

    user = User(
        username=data.username,
        email=str(data.email).lower(),
        password_hash=hash_password(data.password),
    )
    try:
        user_queries.add(db, user)
        response = _create_session(db, user, data.device_name)
        db.commit()
        return response
    except IntegrityError as error:
        db.rollback()
        raise ServiceError(409, "El correo o usuario ya está registrado") from error


def login(db: Session, data: LoginRequest) -> TokenResponse:
    user = user_queries.get_by_email(db, str(data.email))
    if user is None or not verify_password(data.password, user.password_hash):
        raise ServiceError(401, "Credenciales incorrectas")
    try:
        response = _create_session(db, user, data.device_name)
        db.commit()
        return response
    except IntegrityError as error:
        db.rollback()
        raise ServiceError(409, "No fue posible crear la sesión") from error


def refresh_tokens(db: Session, data: RefreshRequest) -> TokenResponse:
    now = datetime.now(timezone.utc)
    token = session_queries.get_refresh_token_by_hash(
        db, hash_refresh_token(data.refresh_token), lock=True
    )
    if token is None:
        raise ServiceError(401, "Refresh token inválido")

    auth_session = token.session
    if token.used_at is not None or token.revoked_at is not None:
        auth_session.revoked_at = now
        db.commit()
        raise ServiceError(401, "Se detectó la reutilización de un refresh token")

    if auth_session.revoked_at is not None or is_session_expired(auth_session, now):
        auth_session.revoked_at = auth_session.revoked_at or now
        token.revoked_at = now
        db.commit()
        raise ServiceError(401, "La sesión expiró o fue revocada")

    try:
        new_raw_token, new_token = _issue_refresh_token(db, auth_session)
        token.used_at = now
        token.replaced_by_id = new_token.id_refresh_token
        auth_session.last_used_at = now
        db.commit()
        return TokenResponse(
            access_token=create_access_token(
                auth_session.id_user, auth_session.id_session
            ),
            refresh_token=new_raw_token,
        )
    except IntegrityError as error:
        db.rollback()
        raise ServiceError(409, "No fue posible renovar la sesión") from error


def logout(db: Session, data: RefreshRequest) -> None:
    token = session_queries.get_refresh_token_by_hash(
        db, hash_refresh_token(data.refresh_token), lock=True
    )
    if token is None:
        return
    now = datetime.now(timezone.utc)
    token.revoked_at = token.revoked_at or now
    token.session.revoked_at = token.session.revoked_at or now
    db.commit()


def logout_all(db: Session, user_id: UUID) -> None:
    session_queries.revoke_all_by_user(db, user_id, datetime.now(timezone.utc))
    db.commit()
