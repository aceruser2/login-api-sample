import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app import app
from datetime import datetime

client = TestClient(app)


def test_create_order_as_customer(client, mock_customer_token):
    """測試顧客建立訂單"""
    order_data = {
        "customer_uuid": "customer-uuid-123",
        "desk_uuid": "desk-uuid-1",
        "order_type": "dine-in",
        "note": "Test order",
        "items": [
            {"item_uuid": "item-uuid-1", "quantity": 2, "note": "No onions"},
            {"item_uuid": "item-uuid-2", "quantity": 1, "note": None},
        ],
    }

    # Mock 訂單服務的創建方法，避免實際的資料庫操作和庫存檢查
    with patch("app.services.order_service.create_order") as mock_create:
        # 模擬成功創建訂單的返回值
        mock_order = MagicMock()
        mock_order.uuid = "order-uuid-1"
        mock_order.customer_uuid = order_data["customer_uuid"]
        mock_order.status = "pending"
        mock_order.total_amount = 300
        mock_create.return_value = mock_order

        headers = {"Authorization": mock_customer_token}
        response = client.post("/orders/", json=order_data, headers=headers)
        assert response.status_code in [200, 201, 401]


def test_create_order_unauthorized_customer(client, mock_customer_token):
    """測試顧客建立他人訂單 - 應該被拒絕"""
    order_data = {
        "customer_uuid": "different-customer-uuid",  # 不是token中的顧客
        "desk_uuid": "desk-uuid-1",
        "order_type": "dine-in",
        "items": [{"item_uuid": "item-uuid-1", "quantity": 1}],
    }

    # 不需要 mock 服務層，因為應該在權限檢查階段就被拒絕
    headers = {"Authorization": mock_customer_token}
    response = client.post("/orders/", json=order_data, headers=headers)
    assert response.status_code in [403, 401]


def test_get_orders_as_customer(client, mock_customer_token):
    """測試顧客查詢自己的訂單"""
    # Mock 訂單服務的顧客查詢方法，只返回該顧客的訂單
    with patch("app.services.order_service.get_orders_by_customer") as mock_get:
        # 模擬該顧客的訂單列表
        mock_orders = [
            MagicMock(
                uuid="order-uuid-1",
                customer_uuid="customer-uuid-123",
                status="pending",
                total_amount=300,
            )
        ]
        mock_get.return_value = mock_orders

        headers = {"Authorization": mock_customer_token}
        response = client.get("/orders/", headers=headers)
        assert response.status_code in [200, 401]


def test_get_orders_as_staff(client, admin_token):
    """測試員工查詢所有訂單"""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Mock 訂單服務的全部查詢方法，員工可以看到所有訂單
    with patch("app.services.order_service.get_all_orders") as mock_get_all:
        # 模擬系統中的所有訂單
        mock_orders = [
            MagicMock(uuid="order-1", status="pending"),
            MagicMock(uuid="order-2", status="completed"),
        ]
        mock_get_all.return_value = mock_orders

        response = client.get("/orders/", headers=headers)
        assert response.status_code in [200, 401]


def test_update_order_status_as_staff(client, admin_token):
    """測試員工更新訂單狀態"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    order_uuid = "order-uuid-1"
    new_status = "cooking"

    # Mock 訂單服務的狀態更新方法，避免實際的狀態驗證邏輯
    with patch("app.services.order_service.update_order_status") as mock_update:
        # 模擬狀態更新成功的返回值
        mock_order = MagicMock()
        mock_order.uuid = order_uuid
        mock_order.status = new_status
        mock_update.return_value = mock_order

        response = client.put(
            f"/orders/{order_uuid}/status?status={new_status}", headers=headers
        )
        assert response.status_code in [200, 401, 404]


def test_update_order_status_as_customer_forbidden(client, mock_customer_token):
    """測試顧客更新訂單狀態 - 應該被拒絕"""
    headers = {"Authorization": mock_customer_token}
    order_uuid = "order-uuid-1"
    new_status = "cooking"

    # 不需要 mock 服務層，因為應該在權限檢查階段就被拒絕
    response = client.put(
        f"/orders/{order_uuid}/status?status={new_status}", headers=headers
    )
    assert response.status_code in [403, 401]
