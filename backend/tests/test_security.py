import time

import jwt
import pytest

from app.core.exceptions import InvalidTokenError
from app.core.security import create_access_token, decode_access_token, hash_password, verify_password


def test_hash_password_does_not_store_plaintext():
    hashed = hash_password("super-secret-1")
    assert hashed != "super-secret-1"
    assert hashed.startswith("$2b$")


def test_verify_password_accepts_correct_password():
    hashed = hash_password("super-secret-1")
    assert verify_password("super-secret-1", hashed) is True


def test_verify_password_rejects_wrong_password():
    hashed = hash_password("super-secret-1")
    assert verify_password("wrong-password", hashed) is False


def test_verify_password_rejects_garbage_hash_without_raising():
    assert verify_password("anything", "not-a-real-hash") is False


def test_decode_access_token_round_trips_subject():
    token = create_access_token(subject="42")
    payload = decode_access_token(token)
    assert payload["sub"] == "42"


def test_decode_access_token_rejects_expired_token():
    token = create_access_token(subject="42", expires_minutes=-1)
    with pytest.raises(InvalidTokenError):
        decode_access_token(token)


def test_decode_access_token_rejects_malformed_token():
    with pytest.raises(InvalidTokenError):
        decode_access_token("this.is.not-a-valid-jwt")


def test_decode_access_token_rejects_token_signed_with_wrong_secret():
    forged = jwt.encode({"sub": "1"}, "a-different-secret", algorithm="HS256")
    with pytest.raises(InvalidTokenError):
        decode_access_token(forged)
