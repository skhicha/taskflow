from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, InvalidCredentialsError, InvalidTokenError
from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def signup(self, email: str, full_name: str, password: str) -> User:
        if self.users.get_by_email(email):
            raise ConflictError(f"an account with email '{email}' already exists")
        hashed = hash_password(password)
        user = self.users.create(email=email, full_name=full_name, hashed_password=hashed)
        self.db.commit()
        return user

    def authenticate(self, email: str, password: str) -> User:
        user = self.users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("invalid email or password")
        return user

    def login(self, email: str, password: str) -> str:
        user = self.authenticate(email, password)
        return create_access_token(subject=str(user.id))

    def get_current_user(self, token: str) -> User:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise InvalidTokenError("token missing subject claim")
        user = self.users.get(int(user_id))
        if user is None:
            raise InvalidTokenError("token subject no longer exists")
        return user
