from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FolderCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    parent_folder_id: UUID | None = None
    color: str | None = Field(default=None, max_length=50)
    icon: str | None = Field(default=None, max_length=100)


class FolderUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    parent_folder_id: UUID | None = None
    color: str | None = Field(default=None, max_length=50)
    icon: str | None = Field(default=None, max_length=100)


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
