from fastapi import APIRouter, status

from API.dependencies import DbSession
from SCHEMAS.auth import LoginRequest, RegisterRequest, TokenResponse
from SCHEMAS.users import UserResponse
from SERVICES import auth


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: DbSession):
    return auth.register_user(db, data)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: DbSession):
    return auth.login(db, data)
