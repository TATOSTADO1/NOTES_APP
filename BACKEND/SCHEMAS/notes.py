from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class NotesCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str | None = None
    id_folder: UUID | None = None

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El título no puede estar vacío")
        return value


class NotesUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    content: str | None = None
    id_folder: UUID | None = None
    favorite: bool | None = None

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("El título no puede estar vacío")
        return value


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


class NotesPage(BaseModel):
    items: list[NotesResponse]
    total: int
    limit: int
    offset: int
