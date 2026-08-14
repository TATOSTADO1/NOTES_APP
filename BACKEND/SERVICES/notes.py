from uuid import UUID

from sqlalchemy.orm import Session

from MODELS.note import Note
from QUERYS import folder as folder_queries
from QUERYS import notes as note_queries
from SCHEMAS.notes import NotesCreate, NotesUpdate
from SERVICES.errors import ServiceError


def _get_owned(
    db: Session, user_id: UUID, note_id: UUID, include_deleted: bool = False
) -> Note:
    note = note_queries.get_by_id_and_user(db, note_id, user_id, include_deleted)
    if note is None:
        raise ServiceError(404, "Nota no encontrada")
    return note


def _validate_folder(db: Session, user_id: UUID, folder_id: UUID | None) -> None:
    if folder_id is not None and folder_queries.get_by_id_and_user(db, folder_id, user_id) is None:
        raise ServiceError(404, "Carpeta no encontrada")


def create_note(db: Session, user_id: UUID, data: NotesCreate) -> Note:
    _validate_folder(db, user_id, data.id_folder)
    note = Note(id_user=user_id, title=data.title.strip(), **data.model_dump(exclude={"title"}))
    note_queries.add(db, note)
    db.commit()
    db.refresh(note)
    return note


def list_notes(
    db: Session, user_id: UUID, *, deleted: bool = False, favorite: bool | None = None
) -> list[Note]:
    return note_queries.get_by_user(db, user_id, deleted=deleted, favorite=favorite)


def get_note(db: Session, user_id: UUID, note_id: UUID) -> Note:
    return _get_owned(db, user_id, note_id)


def update_note(db: Session, user_id: UUID, note_id: UUID, data: NotesUpdate) -> Note:
    note = _get_owned(db, user_id, note_id)
    changes = data.model_dump(exclude_unset=True)
    if "id_folder" in changes:
        _validate_folder(db, user_id, changes["id_folder"])
    if "title" in changes:
        changes["title"] = changes["title"].strip()
    for field, value in changes.items():
        setattr(note, field, value)
    db.commit()
    db.refresh(note)
    return note


def move_to_trash(db: Session, user_id: UUID, note_id: UUID) -> Note:
    note = _get_owned(db, user_id, note_id)
    note.deleted = True
    db.commit()
    db.refresh(note)
    return note


def restore_note(db: Session, user_id: UUID, note_id: UUID) -> Note:
    note = _get_owned(db, user_id, note_id, include_deleted=True)
    note.deleted = False
    db.commit()
    db.refresh(note)
    return note


def delete_permanently(db: Session, user_id: UUID, note_id: UUID) -> None:
    note = _get_owned(db, user_id, note_id, include_deleted=True)
    if not note.deleted:
        raise ServiceError(409, "La nota debe estar en la papelera antes de eliminarla")
    note_queries.delete(db, note)
    db.commit()


def search_notes(db: Session, user_id: UUID, text: str) -> list[Note]:
    return note_queries.search(db, user_id, text.strip())
