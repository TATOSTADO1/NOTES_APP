from uuid import UUID

from sqlalchemy import exists, func, or_, select
from sqlalchemy.orm import Session

from MODELS.note import Note


def get_by_id_and_user(
    db: Session, note_id: UUID, user_id: UUID, include_deleted: bool = False
) -> Note | None:
    statement = select(Note).where(Note.id_note == note_id, Note.id_user == user_id)
    if not include_deleted:
        statement = statement.where(Note.deleted.is_(False))
    return db.scalar(statement)

def get_by_user(
    db: Session,
    user_id: UUID,
    *,
    deleted: bool = False,
    favorite: bool | None = None,
    folder_id: UUID | None = None,
    unfiled: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Note], int]:
    statement = select(Note).where(Note.id_user == user_id, Note.deleted.is_(deleted))
    if favorite is not None:
        statement = statement.where(Note.favorite.is_(favorite))
    if folder_id is not None:
        statement = statement.where(Note.id_folder == folder_id)
    elif unfiled:
        statement = statement.where(Note.id_folder.is_(None))

    total = db.scalar(select(func.count()).select_from(statement.subquery())) or 0
    items = list(
        db.scalars(
            statement.order_by(Note.updated_at.desc()).offset(offset).limit(limit)
        ).all()
    )
    return items, total


def get_by_folder(db: Session, folder_id: UUID, user_id: UUID) -> list[Note]:
    statement = select(Note).where(
        Note.id_folder == folder_id,
        Note.id_user == user_id,
        Note.deleted.is_(False),
    )
    return list(db.scalars(statement.order_by(Note.updated_at.desc())).all())


def has_any_in_folder(db: Session, folder_id: UUID, user_id: UUID) -> bool:
    return bool(
        db.scalar(
            select(
                exists().where(Note.id_folder == folder_id, Note.id_user == user_id)
            )
        )
    )


def search(
    db: Session, user_id: UUID, text: str, *, limit: int = 50, offset: int = 0
) -> tuple[list[Note], int]:
    pattern = f"%{text}%"
    statement = select(Note).where(
        Note.id_user == user_id,
        Note.deleted.is_(False),
        or_(Note.title.ilike(pattern), Note.content.ilike(pattern)),
    )
    total = db.scalar(select(func.count()).select_from(statement.subquery())) or 0
    items = list(
        db.scalars(
            statement.order_by(Note.updated_at.desc()).offset(offset).limit(limit)
        ).all()
    )
    return items, total


def add(db: Session, note: Note) -> Note:
    db.add(note)
    db.flush()
    return note


def delete(db: Session, note: Note) -> None:
    db.delete(note)
