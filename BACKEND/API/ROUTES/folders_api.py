from uuid import UUID

from fastapi import APIRouter, Response, status

from API.dependencies import CurrentUser, DbSession
from SCHEMAS.folders import FolderCreate, FolderResponse, FolderUpdate
from SERVICES import folders


router = APIRouter(prefix="/folders", tags=["Folders"])


@router.post("", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
def create_folder(data: FolderCreate, db: DbSession, current_user: CurrentUser):
    return folders.create_folder(db, current_user.id_user, data)


@router.get("", response_model=list[FolderResponse])
def list_folders(db: DbSession, current_user: CurrentUser):
    return folders.list_folders(db, current_user.id_user)


@router.get("/{folder_id}", response_model=FolderResponse)
def get_folder(folder_id: UUID, db: DbSession, current_user: CurrentUser):
    return folders.get_folder(db, current_user.id_user, folder_id)


@router.patch("/{folder_id}", response_model=FolderResponse)
def update_folder(
    folder_id: UUID, data: FolderUpdate, db: DbSession, current_user: CurrentUser
):
    return folders.update_folder(db, current_user.id_user, folder_id, data)


@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_folder(folder_id: UUID, db: DbSession, current_user: CurrentUser):
    folders.delete_folder(db, current_user.id_user, folder_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
