import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app import app
from datetime import datetime

client = TestClient(app)


@pytest.fixture
def mock_order_data():
    return {
        "customer_uuid": "customer-uuid-1",
        "desk_uuid": "desk-uuid-1",
        "order_type": "dine-in",
        "note": "Test order",
        "items": [
            {"item_uuid": "item-uuid-1", "quantity": 2, "note": "No onions"},
            {"item_uuid": "item-uuid-2", "quantity": 1, "note": None},
        ],
    }


@pytest.fixture
def mock_auth_header():
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def mock_current_user():
    user = MagicMock()
    user.uuid = "customer-uuid-1"
    user.user_status = 2  # Customer
    return user


def test_create_order_success(mock_order_data, mock_auth_header, monkeypatch):
    """測試成功建立訂單"""

    # Mock current_user
    def mock_get_current_user(*args, **kwargs):
        user = MagicMock()
        user.uuid = "customer-uuid-1"
        return user

    # Mock service response
    def mock_create_order(*args, **kwargs):
        return {
            "uuid": "order-uuid-1",
            "customer_uuid": mock_order_data["customer_uuid"],
            "desk_uuid": mock_order_data["desk_uuid"],
            "total_amount": 300,
            "status": "pending",
            "order_type": mock_order_data["order_type"],
            "note": mock_order_data["note"],
            "items": [],
            "create_dt": datetime.now(),
            "update_dt": datetime.now(),
        }

    with patch(
        "app.extension.jwt_config.get_current_user", mock_get_current_user
    ), patch("app.services.order_service.create_order", mock_create_order):
        response = client.post(
            "/orders/", json=mock_order_data, headers=mock_auth_header
        )
        assert response.status_code == 200
        assert response.json()["uuid"] == "order-uuid-1"
        assert response.json()["status"] == "pending"


def test_create_order_unauthorized(mock_order_data, mock_auth_header, monkeypatch):
    """測試建立訂單 - 顧客UUID不匹配"""

    def mock_get_current_user(*args, **kwargs):
        user = MagicMock()
        user.uuid = "different-customer-uuid"  # Different from order's customer_uuid
        return user

    with patch("app.extension.jwt_config.get_current_user", mock_get_current_user):
        response = client.post(
            "/orders/", json=mock_order_data, headers=mock_auth_header
        )
        assert response.status_code == 403
        assert "Can only create orders for yourself" in response.json()["detail"]


def test_get_orders_as_customer(mock_auth_header, monkeypatch):
    """測試顧客查詢自己的訂單"""

    def mock_get_current_user(*args, **kwargs):
        user = MagicMock()
        user.uuid = "customer-uuid-1"
        user.user_status = 2  # Customer
        return user

    def mock_get_orders(*args, **kwargs):
        return [
            {
                "uuid": "order-uuid-1",
                "customer_uuid": "customer-uuid-1",
                "desk_uuid": "desk-uuid-1",
                "total_amount": 300,
                "status": "pending",
                "order_type": "dine-in",
                "note": "Test order",
                "items": [],
                "create_dt": datetime.now(),
                "update_dt": datetime.now(),
            },
            {
                "uuid": "order-uuid-2",
                "customer_uuid": "different-customer",
                "desk_uuid": "desk-uuid-2",
                "total_amount": 500,
                "status": "completed",
                "order_type": "dine-in",
                "note": "Another order",
                "items": [],
                "create_dt": datetime.now(),
                "update_dt": datetime.now(),
            },
        ]

    with patch(
        "app.extension.jwt_config.get_current_user", mock_get_current_user
    ), patch("app.services.order_service.get_orders", mock_get_orders):
        response = client.get("/orders/", headers=mock_auth_header)
        assert response.status_code == 200
        # 顧客只能看到自己的訂單
        assert len(response.json()) == 1
        assert response.json()[0]["uuid"] == "order-uuid-1"


def test_update_order_status_as_staff(mock_auth_header, monkeypatch):
    """測試員工更新訂單狀態"""

    def mock_get_current_user(*args, **kwargs):
        user = MagicMock()
        user.user_status = 1  # Staff
        return user

    def mock_update_status(*args, **kwargs):
        return {
            "uuid": "order-uuid-1",
            "status": "cooking",
            "update_dt": datetime.now(),
        }

    with patch(
        "app.extension.jwt_config.get_current_user", mock_get_current_user
    ), patch("app.services.order_service.update_order_status", mock_update_status):
        response = client.put(
            "/orders/order-uuid-1/status?status=cooking", headers=mock_auth_header
        )
        assert response.status_code == 200
        assert response.json()["status"] == "cooking"


def test_update_order_status_as_customer(mock_auth_header, monkeypatch):
    """測試顧客更新訂單狀態 - 應該被拒絕"""

    def mock_get_current_user(*args, **kwargs):
        user = MagicMock()
        user.user_status = 2  # Customer
        return user

    with patch("app.extension.jwt_config.get_current_user", mock_get_current_user):
        response = client.put(
            "/orders/order-uuid-1/status?status=cooking", headers=mock_auth_header
        )
        assert response.status_code == 403
        assert "Only staff can update order status" in response.json()["detail"]
