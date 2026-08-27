from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.deps import AdminUser, CurrentUser, DbSession
from app.schemas.auth import Token, UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token, summary="Login and obtain JWT token")
def login(db: DbSession, form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    token = AuthService(db).authenticate(form_data.username, form_data.password)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return token


@router.get("/me", response_model=UserResponse, summary="Get current user profile")
def me(user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(user)


@router.post("/users", response_model=UserResponse, summary="Create user (admin only)")
def create_user(data: UserCreate, db: DbSession, _: AdminUser) -> UserResponse:
    if AuthService(db).user_repo.get_by_username(data.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    return AuthService(db).create_user(data)


@router.get("/users", response_model=list[UserResponse], summary="List users (admin only)")
def list_users(db: DbSession, _: AdminUser) -> list[UserResponse]:
    return AuthService(db).list_users()
