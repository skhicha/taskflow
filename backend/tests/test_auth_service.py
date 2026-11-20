import pytest

from app.core.exceptions import ConflictError, InvalidCredentialsError, InvalidTokenError
from app.core.security import create_access_token


def test_signup_creates_user_with_hashed_password(auth_service):
    user = auth_service.signup("new@example.com", "New User", "password123")
    assert user.id is not None
    assert user.email == "new@example.com"
    assert user.hashed_password != "password123"


def test_signup_lowercases_email_for_lookup(auth_service):
    auth_service.signup("Mixed@Example.com", "Mixed Case", "password123")
    user = auth_service.users.get_by_email("mixed@example.com")
    assert user is not None


def test_duplicate_signup_raises_conflict(auth_service):
    auth_service.signup("dupe@example.com", "First", "password123")
    with pytest.raises(ConflictError):
        auth_service.signup("dupe@example.com", "Second", "password456")


def test_login_returns_token_for_correct_credentials(auth_service):
    auth_service.signup("login@example.com", "Login User", "password123")
    token = auth_service.login("login@example.com", "password123")
    assert isinstance(token, str) and len(token) > 0


def test_login_rejects_wrong_password(auth_service):
    auth_service.signup("login2@example.com", "Login User", "password123")
    with pytest.raises(InvalidCredentialsError):
        auth_service.login("login2@example.com", "wrong-password")


def test_login_rejects_unknown_email(auth_service):
    with pytest.raises(InvalidCredentialsError):
        auth_service.login("nobody@example.com", "whatever123")


def test_get_current_user_returns_user_for_valid_token(auth_service):
    user = auth_service.signup("me@example.com", "Me", "password123")
    token = create_access_token(subject=str(user.id))
    fetched = auth_service.get_current_user(token)
    assert fetched.id == user.id


def test_get_current_user_rejects_expired_token(auth_service):
    user = auth_service.signup("expired@example.com", "Exp", "password123")
    token = create_access_token(subject=str(user.id), expires_minutes=-1)
    with pytest.raises(InvalidTokenError):
        auth_service.get_current_user(token)


def test_get_current_user_rejects_invalid_token(auth_service):
    with pytest.raises(InvalidTokenError):
        auth_service.get_current_user("garbage-token")


def test_get_current_user_rejects_token_for_deleted_user(auth_service):
    token = create_access_token(subject="999999")
    with pytest.raises(InvalidTokenError):
        auth_service.get_current_user(token)
