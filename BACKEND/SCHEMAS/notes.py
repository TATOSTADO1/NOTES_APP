from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NotesCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str | None = None
    id_folder: UUID | None = None


class NotesUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    content: str | None = None
    id_folder: UUID | None = None
    favorite: bool | None = None


class NotesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_note: UUID
    title: str
    content: str | None
    id_folder: UUID | None
    id_user: UUID
    favorite: bool
    deleted: bool
    created_at: datetime
    updated_at: datetime
