from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FolderCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    parent_folder_id: UUID | None = None
    color: str | None = Field(default=None, max_length=50)
    icon: str | None = Field(default=None, max_length=100)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El nombre no puede estar vacío")
        return value


class FolderUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    parent_folder_id: UUID | None = None
    color: str | None = Field(default=None, max_length=50)
    icon: str | None = Field(default=None, max_length=100)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("El nombre no puede estar vacío")
        return value


class FolderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_folder: UUID
    name: str
    parent_folder_id: UUID | None
    color: str | None
    icon: str | None
    id_user: UUID
    created_at: datetime
    updated_at: datetime
