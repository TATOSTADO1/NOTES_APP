from fastapi import APIRouter, Response, status

from API.dependencies import CurrentUser, DbSession
from SCHEMAS.users import PasswordChange, UserResponse, UserUpdate
from SERVICES import users


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user: CurrentUser):
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_me(data: UserUpdate, db: DbSession, current_user: CurrentUser):
    return users.update_profile(db, current_user.id_user, data)


@router.post("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(data: PasswordChange, db: DbSession, current_user: CurrentUser):
    users.change_password(db, current_user.id_user, data)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
