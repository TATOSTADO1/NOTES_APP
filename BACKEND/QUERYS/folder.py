from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from MODELS.folder import Folder


def get_by_id_and_user(db: Session, folder_id: UUID, user_id: UUID) -> Folder | None:
    return db.scalar(
        select(Folder).where(Folder.id_folder == folder_id, Folder.id_user == user_id)
    )


def get_by_user(db: Session, user_id: UUID) -> list[Folder]:
    return list(
        db.scalars(
            select(Folder).where(Folder.id_user == user_id).order_by(Folder.name)
        ).all()
    )


def get_children(db: Session, parent_id: UUID, user_id: UUID) -> list[Folder]:
    return list(
        db.scalars(
            select(Folder).where(
                Folder.parent_folder_id == parent_id, Folder.id_user == user_id
            )
        ).all()
    )


def get_by_name(
    db: Session, user_id: UUID, name: str, parent_folder_id: UUID | None
) -> Folder | None:
    parent_filter = (
        Folder.parent_folder_id.is_(None)
        if parent_folder_id is None
        else Folder.parent_folder_id == parent_folder_id
    )
    return db.scalar(
        select(Folder).where(
            Folder.id_user == user_id, Folder.name == name, parent_filter
        )
    )


def add(db: Session, folder: Folder) -> Folder:
    db.add(folder)
    db.flush()
    return folder


def delete(db: Session, folder: Folder) -> None:
    db.delete(folder)
