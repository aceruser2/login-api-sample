import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app import app
from app.extension.redis_utils import (
    generate_verification_code,
    store_verification_code,
    verify_code,
)

client = TestClient(app)


@pytest.fixture
def mock_staff_credentials():
    return {"username": "admin", "password": "123456"}


@pytest.fixture
def mock_customer_data():
    return {
        "custom_name": "Test User",
        "phone": "1234567890",
        "email": "test@example.com",
    }


@pytest.fixture
def mock_verification():
    return {
        "email": "test@example.com",
        "verify_code": "123456",
        "desk_uuid": "desk-uuid-1",
    }


@pytest.fixture
def mock_takeout_verification():
    return {"email": "test@example.com", "verify_code": "123456", "phone": "1234567890"}


def test_staff_login_success(mock_staff_credentials, monkeypatch):
    """測試員工登入成功"""

    # 模擬服務層返回值，避免實際數據庫查詢
    def mock_get_user(*args, **kwargs):
        mock_user = MagicMock()
        mock_user.uuid = "user-uuid-1"
        mock_user.check_password.return_value = True
        return mock_user

    def mock_get_permissions(*args, **kwargs):
        return []

    with patch("app.services.user_service.get_user_by_username", mock_get_user), patch(
        "app.services.user_service.get_user_all_role_and_permission_by_user_uuid",
        mock_get_permissions,
    ):
        response = client.post("/token/staff", json=mock_staff_credentials)
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()
        assert response.json()["token_type"] == "bearer"


def test_staff_login_invalid_credentials(mock_staff_credentials, monkeypatch):
    """測試員工登入失敗 - 密碼錯誤"""

    def mock_get_user(*args, **kwargs):
        mock_user = MagicMock()
        mock_user.check_password.return_value = False
        return mock_user

    with patch("app.services.user_service.get_user_by_username", mock_get_user):
        response = client.post("/token/staff", json=mock_staff_credentials)
        assert response.status_code == 401
        assert "Incorrect password" in response.json()["detail"]


def test_email_verification_send(mock_customer_data, monkeypatch):
    """測試發送電子郵件驗證碼"""

    def mock_get_customer(*args, **kwargs):
        return None

    def mock_create_customer(*args, **kwargs):
        mock_cust = MagicMock()
        mock_cust.uuid = "cust-uuid-1"
        return mock_cust

    def mock_send_email(*args, **kwargs):
        return True

    def mock_can_send_code(*args, **kwargs):
        return True

    with patch(
        "app.services.custom_service.get_customer_by_email", mock_get_customer
    ), patch(
        "app.services.custom_service.create_customer", mock_create_customer
    ), patch(
        "app.extension.redis_utils.can_send_new_code", mock_can_send_code
    ), patch(
        "app.services.email_service.send_verification_email", mock_send_email
    ):
        response = client.post("/custom/email-send-code", json=mock_customer_data)
        assert response.status_code == 200
        assert "message" in response.json()
        assert "require_verification" in response.json()
        assert response.json()["is_new_user"] == True


def test_dine_in_verification(mock_verification, monkeypatch):
    """測試內用驗證成功"""

    def mock_verify(*args, **kwargs):
        return True

    def mock_get_customer(*args, **kwargs):
        mock_cust = MagicMock()
        mock_cust.uuid = "cust-uuid-1"
        mock_cust.is_verified = False
        return mock_cust

    def mock_get_desk(*args, **kwargs):
        mock_desk = MagicMock()
        mock_desk.uuid = "desk-uuid-1"
        return mock_desk

    def mock_bind_desk(*args, **kwargs):
        mock_binding = MagicMock()
        mock_binding.desk_uuid = "desk-uuid-1"
        return mock_binding

    with patch("app.extension.redis_utils.verify_code", mock_verify), patch(
        "app.services.custom_service.get_customer_by_email", mock_get_customer
    ), patch("app.services.desk_service.get_desk_by_uuid", mock_get_desk), patch(
        "app.services.custom_service.get_active_binding", return_value=None
    ), patch(
        "app.services.custom_service.bind_desk_to_customer", mock_bind_desk
    ):
        response = client.post("/verify/dine-in", json=mock_verification)
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()


def test_takeout_verification(mock_takeout_verification, monkeypatch):
    """測試外帶驗證成功"""

    def mock_verify(*args, **kwargs):
        return True

    def mock_get_customer(*args, **kwargs):
        mock_cust = MagicMock()
        mock_cust.uuid = "cust-uuid-1"
        mock_cust.is_verified = False
        return mock_cust

    with patch("app.extension.redis_utils.verify_code", mock_verify), patch(
        "app.services.custom_service.get_customer_by_email", mock_get_customer
    ):
        response = client.post("/verify/takeout", json=mock_takeout_verification)
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()
