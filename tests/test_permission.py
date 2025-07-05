import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app import app
from datetime import datetime

client = TestClient(app)


@pytest.fixture
def mock_staff_token():
    """模擬員工令牌"""
    return "Bearer staff-token"


@pytest.fixture
def mock_customer_token():
    """模擬顧客令牌"""
    return "Bearer customer-token"


@pytest.fixture
def mock_staff_user():
    """模擬員工用戶"""
    user = MagicMock()
    user.uuid = "staff-uuid"
    user.user_status = 1  # Staff
    return user


@pytest.fixture
def mock_customer_user():
    """模擬顧客用戶"""
    user = MagicMock()
    user.uuid = "customer-uuid"
    user.user_status = 2  # Customer
    return user


def test_customer_cannot_process_payment(mock_customer_token, mock_customer_user):
    """測試顧客不能處理支付"""
    payment_data = {
        "order_uuid": "order-uuid-1",
        "payment_method": "cash",
        "amount_paid": 500,
        "payment_note": "test payment",
    }

    with patch(
        "app.extension.jwt_config.get_current_user", return_value=mock_customer_user
    ):
        response = client.post(
            "/payments/",
            json=payment_data,
            headers={"Authorization": mock_customer_token},
        )
        assert response.status_code == 403
        assert "Only staff can process payments" in response.json()["detail"]


def test_staff_can_process_payment(mock_staff_token, mock_staff_user):
    """測試員工可以處理支付"""
    payment_data = {
        "order_uuid": "order-uuid-1",
        "payment_method": "cash",
        "amount_paid": 500,
        "payment_note": "test payment",
    }

    def mock_create_payment(*args, **kwargs):
        return MagicMock(
            uuid="payment-uuid",
            order_uuid=payment_data["order_uuid"],
            payment_method=payment_data["payment_method"],
            amount_paid=payment_data["amount_paid"],
            payment_note=payment_data["payment_note"],
            create_dt=datetime.now(),
        )

    with patch(
        "app.extension.jwt_config.get_current_user", return_value=mock_staff_user
    ), patch("app.services.payment_service.create_payment", mock_create_payment):
        response = client.post(
            "/payments/", json=payment_data, headers={"Authorization": mock_staff_token}
        )
        assert response.status_code == 200


def test_customer_cannot_manage_menu(mock_customer_token, mock_customer_user):
    """測試顧客不能管理菜單"""
    menu_data = {
        "name": "Test Burger",
        "description": "Test burger description",
        "price": 120,
        "category": "主餐",
    }

    with patch(
        "app.extension.jwt_config.get_current_user", return_value=mock_customer_user
    ):
        response = client.post(
            "/menu/items/",
            json=menu_data,
            headers={"Authorization": mock_customer_token},
        )
        assert response.status_code == 403
        assert "Only staff can manage menu items" in response.json()["detail"]


def test_customer_can_only_create_own_orders(mock_customer_token, mock_customer_user):
    """測試顧客只能創建自己的訂單"""
    order_data = {
        "customer_uuid": "different-customer-uuid",  # 不是自己的UUID
        "desk_uuid": "desk-uuid-1",
        "order_type": "dine-in",
        "items": [{"item_uuid": "item-uuid-1", "quantity": 1}],
    }

    with patch(
        "app.extension.jwt_config.get_current_user", return_value=mock_customer_user
    ):
        response = client.post(
            "/orders/", json=order_data, headers={"Authorization": mock_customer_token}
        )
        assert response.status_code == 403
        assert "Can only create orders for yourself" in response.json()["detail"]


def test_customer_cannot_update_order_status(mock_customer_token, mock_customer_user):
    """測試顧客不能更新訂單狀態"""
    with patch(
        "app.extension.jwt_config.get_current_user", return_value=mock_customer_user
    ):
        response = client.put(
            "/orders/order-uuid-1/status?status=cooking",
            headers={"Authorization": mock_customer_token},
        )
        assert response.status_code == 403
        assert "Only staff can update order status" in response.json()["detail"]
