from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from CORE.database import get_db
from CORE.encryption import decode_access_token
from MODELS.session import AuthSession
from MODELS.user import User
from QUERYS import sessions as session_queries
from QUERYS import users as user_queries
from SERVICES.auth import is_session_expired


DbSession = Annotated[Session, Depends(get_db)]
bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthContext:
    user: User
    auth_session: AuthSession


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=401,
        detail="Token inválido, expirado o revocado",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_auth_context(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> AuthContext:
    token_data = decode_access_token(credentials.credentials) if credentials else None
    if token_data is None:
        raise _unauthorized()

    auth_session = session_queries.get_by_id(db, token_data.session_id)
    if (
        auth_session is None
        or auth_session.id_user != token_data.user_id
        or auth_session.revoked_at is not None
        or is_session_expired(auth_session, datetime.now(timezone.utc))
    ):
        raise _unauthorized()

    user = user_queries.get_by_id(db, token_data.user_id)
    if user is None:
        raise _unauthorized()
    return AuthContext(user=user, auth_session=auth_session)


Auth = Annotated[AuthContext, Depends(get_auth_context)]


def get_current_user(auth: Auth) -> User:
    return auth.user


def get_current_session(auth: Auth) -> AuthSession:
    return auth.auth_session


CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentSession = Annotated[AuthSession, Depends(get_current_session)]
