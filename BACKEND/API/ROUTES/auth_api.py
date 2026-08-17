from fastapi import APIRouter, Response, status

from API.dependencies import CurrentUser, DbSession
from SCHEMAS.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from SERVICES import auth


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: DbSession):
    return auth.register_user(db, data)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: DbSession):
    return auth.login(db, data)


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, db: DbSession):
    return auth.refresh_tokens(db, data)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(data: RefreshRequest, db: DbSession):
    auth.logout(db, data)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
def logout_all(db: DbSession, current_user: CurrentUser):
    auth.logout_all(db, current_user.id_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
