from uuid import UUID

from fastapi import APIRouter, Query, Response, status

from API.dependencies import CurrentUser, DbSession
from SCHEMAS.notes import NotesCreate, NotesPage, NotesResponse, NotesUpdate
from SERVICES import notes


router = APIRouter(prefix="/notes", tags=["Notes"])


@router.post("", response_model=NotesResponse, status_code=status.HTTP_201_CREATED)
def create_note(data: NotesCreate, db: DbSession, current_user: CurrentUser):
    return notes.create_note(db, current_user.id_user, data)


@router.get("", response_model=NotesPage)
def list_notes(
    db: DbSession,
    current_user: CurrentUser,
    deleted: bool = False,
    favorite: bool | None = None,
    folder_id: UUID | None = None,
    unfiled: bool = False,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return notes.list_notes(
        db,
        current_user.id_user,
        deleted=deleted,
        favorite=favorite,
        folder_id=folder_id,
        unfiled=unfiled,
        limit=limit,
        offset=offset,
    )


@router.get("/search", response_model=NotesPage)
def search_notes(
    db: DbSession,
    current_user: CurrentUser,
    q: str = Query(min_length=1, max_length=255),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return notes.search_notes(
        db, current_user.id_user, q, limit=limit, offset=offset
    )


@router.get("/{note_id}", response_model=NotesResponse)
def get_note(note_id: UUID, db: DbSession, current_user: CurrentUser):
    return notes.get_note(db, current_user.id_user, note_id)


@router.patch("/{note_id}", response_model=NotesResponse)
def update_note(
    note_id: UUID, data: NotesUpdate, db: DbSession, current_user: CurrentUser
):
    return notes.update_note(db, current_user.id_user, note_id, data)


@router.post("/{note_id}/trash", response_model=NotesResponse)
def trash_note(note_id: UUID, db: DbSession, current_user: CurrentUser):
    return notes.move_to_trash(db, current_user.id_user, note_id)


@router.post("/{note_id}/restore", response_model=NotesResponse)
def restore_note(note_id: UUID, db: DbSession, current_user: CurrentUser):
    return notes.restore_note(db, current_user.id_user, note_id)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: UUID, db: DbSession, current_user: CurrentUser):
    notes.delete_permanently(db, current_user.id_user, note_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
