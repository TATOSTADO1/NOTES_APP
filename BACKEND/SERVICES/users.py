from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from MODELS.user import User
from QUERYS import users as user_queries
from SCHEMAS.users import UserUpdate
from SERVICES.errors import ServiceError


def get_profile(db: Session, user_id: UUID) -> User:
    user = user_queries.get_by_id(db, user_id)
    if user is None:
        raise ServiceError(404, "Usuario no encontrado")
    return user


def update_profile(db: Session, user_id: UUID, data: UserUpdate) -> User:
    user = get_profile(db, user_id)
    changes = data.model_dump(exclude_unset=True)
    if "email" in changes:
        changes["email"] = str(changes["email"]).lower()
        existing = user_queries.get_by_email(db, changes["email"])
        if existing and existing.id_user != user_id:
            raise ServiceError(409, "El correo ya está registrado")
    if "username" in changes:
        existing = user_queries.get_by_username(db, changes["username"])
        if existing and existing.id_user != user_id:
            raise ServiceError(409, "El nombre de usuario ya está registrado")
    for field, value in changes.items():
        setattr(user, field, value)
    try:
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError as error:
        db.rollback()
        raise ServiceError(409, "El correo o usuario ya está registrado") from error
