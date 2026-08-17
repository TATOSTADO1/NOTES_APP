from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from MODELS.note import Note
from QUERYS import folder as folder_queries
from QUERYS import notes as note_queries
from SCHEMAS.notes import NotesCreate, NotesPage, NotesUpdate
from SERVICES.errors import ServiceError


def _get_owned(
    db: Session, user_id: UUID, note_id: UUID, include_deleted: bool = False
) -> Note:
    note = note_queries.get_by_id_and_user(db, note_id, user_id, include_deleted)
    if note is None:
        raise ServiceError(404, "Nota no encontrada")
    return note


def _validate_folder(db: Session, user_id: UUID, folder_id: UUID | None) -> None:
    if (
        folder_id is not None
        and folder_queries.get_by_id_and_user(db, folder_id, user_id) is None
    ):
        raise ServiceError(404, "Carpeta no encontrada")


def _commit(db: Session, note: Note | None = None) -> None:
    try:
        db.commit()
        if note is not None:
            db.refresh(note)
    except IntegrityError as error:
        db.rollback()
        raise ServiceError(409, "La operación sobre la nota no es válida") from error


def create_note(db: Session, user_id: UUID, data: NotesCreate) -> Note:
    _validate_folder(db, user_id, data.id_folder)
    note = Note(id_user=user_id, **data.model_dump())
    note_queries.add(db, note)
    _commit(db, note)
    return note


def list_notes(
    db: Session,
    user_id: UUID,
    *,
    deleted: bool = False,
    favorite: bool | None = None,
    folder_id: UUID | None = None,
    unfiled: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> NotesPage:
    if folder_id is not None and unfiled:
        raise ServiceError(400, "No se puede combinar folder_id con unfiled")
    _validate_folder(db, user_id, folder_id)
    items, total = note_queries.get_by_user(
        db,
        user_id,
        deleted=deleted,
        favorite=favorite,
        folder_id=folder_id,
        unfiled=unfiled,
        limit=limit,
        offset=offset,
    )
    return NotesPage(items=items, total=total, limit=limit, offset=offset)


def get_note(db: Session, user_id: UUID, note_id: UUID) -> Note:
    return _get_owned(db, user_id, note_id)


def update_note(db: Session, user_id: UUID, note_id: UUID, data: NotesUpdate) -> Note:
    note = _get_owned(db, user_id, note_id)
    changes = data.model_dump(exclude_unset=True)
    if "id_folder" in changes:
        _validate_folder(db, user_id, changes["id_folder"])
    for field, value in changes.items():
        setattr(note, field, value)
    _commit(db, note)
    return note


def move_to_trash(db: Session, user_id: UUID, note_id: UUID) -> Note:
    note = _get_owned(db, user_id, note_id)
    note.deleted = True
    _commit(db, note)
    return note


def restore_note(db: Session, user_id: UUID, note_id: UUID) -> Note:
    note = _get_owned(db, user_id, note_id, include_deleted=True)
    note.deleted = False
    _commit(db, note)
    return note


def delete_permanently(db: Session, user_id: UUID, note_id: UUID) -> None:
    note = _get_owned(db, user_id, note_id, include_deleted=True)
    if not note.deleted:
        raise ServiceError(409, "La nota debe estar en la papelera antes de eliminarla")
    note_queries.delete(db, note)
    _commit(db)


def search_notes(
    db: Session, user_id: UUID, text: str, *, limit: int = 50, offset: int = 0
) -> NotesPage:
    text = text.strip()
    if not text:
        raise ServiceError(400, "La búsqueda no puede estar vacía")
    items, total = note_queries.search(
        db, user_id, text, limit=limit, offset=offset
    )
    return NotesPage(items=items, total=total, limit=limit, offset=offset)
