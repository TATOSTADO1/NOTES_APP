from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from CORE.encryption import create_access_token, hash_password, verify_password
from MODELS.user import User
from QUERYS import users as user_queries
from SCHEMAS.auth import LoginRequest, RegisterRequest, TokenResponse
from SERVICES.errors import ServiceError


def register_user(db: Session, data: RegisterRequest) -> User:
    if user_queries.get_by_email(db, str(data.email)):
        raise ServiceError(409, "El correo ya está registrado")
    if user_queries.get_by_username(db, data.username):
        raise ServiceError(409, "El nombre de usuario ya está registrado")

    user = User(
        username=data.username.strip(),
        email=str(data.email).lower(),
        password_hash=hash_password(data.password),
    )
    try:
        user_queries.add(db, user)
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError as error:
        db.rollback()
        raise ServiceError(409, "El correo o usuario ya está registrado") from error


def login(db: Session, data: LoginRequest) -> TokenResponse:
    user = user_queries.get_by_email(db, str(data.email))
    if user is None or not verify_password(data.password, user.password_hash):
        raise ServiceError(401, "Credenciales incorrectas")
    return TokenResponse(access_token=create_access_token(user.id_user), token_type="bearer")
