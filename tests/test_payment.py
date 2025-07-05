import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app import app
from datetime import datetime

client = TestClient(app)


@pytest.fixture
def mock_payment_data():
    return {
        "order_uuid": "order-uuid-1",
        "payment_method": "cash",
        "amount_paid": 500,
        "payment_note": "Customer paid in cash",
    }


@pytest.fixture
def mock_auth_header():
    return {"Authorization": "Bearer test-token"}


def test_process_payment_success(mock_payment_data, mock_auth_header, monkeypatch):
    """測試成功處理支付"""

    def mock_get_current_user(*args, **kwargs):
        return MagicMock()

    def mock_create_payment(*args, **kwargs):
        return {
            "uuid": "payment-uuid-1",
            "order_uuid": mock_payment_data["order_uuid"],
            "payment_method": mock_payment_data["payment_method"],
            "amount_paid": mock_payment_data["amount_paid"],
            "payment_note": mock_payment_data["payment_note"],
            "create_dt": datetime.now(),
        }

    with patch(
        "app.extension.jwt_config.get_current_user", mock_get_current_user
    ), patch("app.services.payment_service.create_payment", mock_create_payment):
        response = client.post(
            "/payments/", json=mock_payment_data, headers=mock_auth_header
        )
        assert response.status_code == 200
        assert response.json()["uuid"] == "payment-uuid-1"
        assert response.json()["payment_method"] == mock_payment_data["payment_method"]


def test_process_payment_insufficient_amount(
    mock_payment_data, mock_auth_header, monkeypatch
):
    """測試支付金額不足"""

    def mock_get_current_user(*args, **kwargs):
        return MagicMock()

    def mock_create_payment(*args, **kwargs):
        raise ValueError("Insufficient payment amount. Required: 600, Provided: 500")

    with patch(
        "app.extension.jwt_config.get_current_user", mock_get_current_user
    ), patch("app.services.payment_service.create_payment", mock_create_payment):
        response = client.post(
            "/payments/", json=mock_payment_data, headers=mock_auth_header
        )
        assert response.status_code == 400
        assert "Insufficient payment amount" in response.json()["detail"]


def test_process_payment_order_not_found(
    mock_payment_data, mock_auth_header, monkeypatch
):
    """測試訂單不存在"""

    def mock_get_current_user(*args, **kwargs):
        return MagicMock()

    def mock_create_payment(*args, **kwargs):
        raise ValueError("Order not found")

    with patch(
        "app.extension.jwt_config.get_current_user", mock_get_current_user
    ), patch("app.services.payment_service.create_payment", mock_create_payment):
        response = client.post(
            "/payments/", json=mock_payment_data, headers=mock_auth_header
        )
        assert response.status_code == 400
        assert "Order not found" in response.json()["detail"]
