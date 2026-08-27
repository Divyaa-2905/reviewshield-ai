from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.auth import Token, UserCreate, UserResponse


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repo = UserRepository(db)

    def authenticate(self, username: str, password: str) -> Token | None:
        user = self.user_repo.get_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            return None
        token = create_access_token({"sub": user.username, "role": user.role.value})
        return Token(access_token=token)

    def create_user(self, data: UserCreate) -> UserResponse:
        role = UserRole(data.role)
        user = self.user_repo.create(
            username=data.username,
            email=data.email,
            hashed_password=get_password_hash(data.password),
            role=role,
        )
        return UserResponse.model_validate(user)

    def list_users(self) -> list[UserResponse]:
        return [UserResponse.model_validate(u) for u in self.user_repo.list_all()]
