from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from MODELS.folder import Folder
from QUERYS import folder as folder_queries
from QUERYS import notes as note_queries
from SCHEMAS.folders import FolderCreate, FolderUpdate
from SERVICES.errors import ServiceError


def _get_owned(db: Session, user_id: UUID, folder_id: UUID) -> Folder:
    folder = folder_queries.get_by_id_and_user(db, folder_id, user_id)
    if folder is None:
        raise ServiceError(404, "Carpeta no encontrada")
    return folder


def _validate_parent(
    db: Session, user_id: UUID, parent_id: UUID | None, folder_id: UUID | None = None
) -> None:
    visited: set[UUID] = set()
    current_id = parent_id
    while current_id is not None:
        if current_id == folder_id or current_id in visited:
            raise ServiceError(400, "La jerarquía de carpetas produciría un ciclo")
        visited.add(current_id)
        current = _get_owned(db, user_id, current_id)
        current_id = current.parent_folder_id


def _commit(db: Session, folder: Folder | None = None) -> None:
    try:
        db.commit()
        if folder is not None:
            db.refresh(folder)
    except IntegrityError as error:
        db.rollback()
        raise ServiceError(409, "La operación sobre la carpeta no es válida") from error


def create_folder(db: Session, user_id: UUID, data: FolderCreate) -> Folder:
    name = data.name
    _validate_parent(db, user_id, data.parent_folder_id)
    if folder_queries.get_by_name(db, user_id, name, data.parent_folder_id):
        raise ServiceError(409, "Ya existe una carpeta con ese nombre en esta ubicación")
    folder = Folder(id_user=user_id, name=name, **data.model_dump(exclude={"name"}))
    folder_queries.add(db, folder)
    _commit(db, folder)
    return folder


def list_folders(db: Session, user_id: UUID) -> list[Folder]:
    return folder_queries.get_by_user(db, user_id)


def get_folder(db: Session, user_id: UUID, folder_id: UUID) -> Folder:
    return _get_owned(db, user_id, folder_id)


def update_folder(
    db: Session, user_id: UUID, folder_id: UUID, data: FolderUpdate
) -> Folder:
    folder = _get_owned(db, user_id, folder_id)
    changes = data.model_dump(exclude_unset=True)
    parent_id = changes.get("parent_folder_id", folder.parent_folder_id)
    _validate_parent(db, user_id, parent_id, folder_id)
    name = changes.get("name", folder.name)
    duplicate = folder_queries.get_by_name(db, user_id, name, parent_id)
    if duplicate and duplicate.id_folder != folder_id:
        raise ServiceError(409, "Ya existe una carpeta con ese nombre en esta ubicación")
    for field, value in changes.items():
        setattr(folder, field, value)
    _commit(db, folder)
    return folder


def delete_folder(db: Session, user_id: UUID, folder_id: UUID) -> None:
    folder = _get_owned(db, user_id, folder_id)
    if folder_queries.get_children(db, folder_id, user_id):
        raise ServiceError(409, "La carpeta contiene subcarpetas")
    if note_queries.has_any_in_folder(db, folder_id, user_id):
        raise ServiceError(409, "La carpeta contiene notas")
    folder_queries.delete(db, folder)
    _commit(db)
