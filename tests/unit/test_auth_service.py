import os

os.environ.setdefault("ALLOW_INSECURE_DEFAULTS", "true")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-at-least-32-chars")
os.environ.setdefault("ADMIN_USERNAME", "testadmin")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword")

from app.services.auth_service import AuthService


def test_authenticate_valid_credentials():
    service = AuthService()
    assert service.authenticate_user("testadmin", "testpassword") is True


def test_authenticate_wrong_password():
    service = AuthService()
    assert service.authenticate_user("testadmin", "wrongpass") is False


def test_authenticate_wrong_username():
    service = AuthService()
    assert service.authenticate_user("hacker", "testpassword") is False


def test_create_and_verify_token():
    service = AuthService()
    token = service.create_access_token({"sub": "testadmin"})
    username = service.verify_token(token)
    assert username == "testadmin"


def test_verify_invalid_token_returns_none():
    service = AuthService()
    assert service.verify_token("not.a.token") is None


def test_hash_and_verify_password():
    from unittest.mock import patch, MagicMock

    mock_ctx = MagicMock()
    mock_ctx.hash.return_value = "$2b$12$fakehash"
    mock_ctx.verify.side_effect = lambda plain, hashed: plain == "mysecret"

    with patch("app.services.auth_service.pwd_context", mock_ctx):
        service = AuthService()
        hashed = service.get_password_hash("mysecret")
        assert service.verify_password("mysecret", hashed) is True
        assert service.verify_password("wrong", hashed) is False
