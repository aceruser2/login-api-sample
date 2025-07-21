import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app import app
from datetime import datetime
from app.extension.emun_setting import OrderStatusEnum

client = TestClient(app)


def test_create_order_as_customer(client, mock_customer_token):
    """測試顧客建立自己的訂單"""
    order_data = {
        "customer_uuid": "customer-uuid-123",  # 與token中的uuid匹配
        "desk_uuid": "desk-uuid-1",
        "order_type": "dine-in",
        "note": "Test order",
        "items": [
            {"item_uuid": "item-uuid-1", "quantity": 2, "note": "No onions"},
            {"item_uuid": "item-uuid-2", "quantity": 1, "note": None},
        ],
    }

    with patch("app.services.order_service.create_order") as mock_create:
        mock_order = MagicMock()
        mock_order.uuid = "order-uuid-1"
        mock_order.customer_uuid = order_data["customer_uuid"]
        mock_order.status = OrderStatusEnum.PENDING.value  # 使用狀態碼
        mock_order.total_amount = 300
        mock_create.return_value = mock_order

        headers = {"Authorization": mock_customer_token}
        response = client.post("/orders/", json=order_data, headers=headers)
        assert response.status_code in [200, 201]


def test_create_order_unauthorized_customer(client, mock_customer_token):
    """測試顧客建立他人訂單 - 應該被拒絕"""
    order_data = {
        "customer_uuid": "different-customer-uuid",  # 不是token中的顧客
        "desk_uuid": "desk-uuid-1",
        "order_type": "dine-in",
        "items": [{"item_uuid": "item-uuid-1", "quantity": 1}],
    }

    headers = {"Authorization": mock_customer_token}
    response = client.post("/orders/", json=order_data, headers=headers)
    assert response.status_code == 403


def test_update_order_as_customer_own_pending(client, mock_customer_token):
    """測試顧客更新自己的pending訂單 - 應該允許"""
    order_uuid = "order-uuid-1"
    update_data = {
        "note": "Updated note",
        "items": [{"item_uuid": "item-uuid-1", "quantity": 3, "note": "Extra spicy"}],
    }

    with patch("app.services.order_service.get_order_by_uuid") as mock_get:
        mock_order = MagicMock()
        mock_order.uuid = order_uuid
        mock_order.customer_uuid = "customer-uuid-123"  # 與token中的uuid匹配
        mock_order.status = OrderStatusEnum.PENDING.value  # pending
        mock_get.return_value = mock_order

        with patch("app.services.order_service.update_order") as mock_update:
            mock_update.return_value = mock_order

            headers = {"Authorization": mock_customer_token}
            response = client.put(
                f"/orders/{order_uuid}", json=update_data, headers=headers
            )
            assert response.status_code == 200


def test_update_order_as_customer_non_pending(client, mock_customer_token):
    """測試顧客更新自己的非pending訂單 - 應該被拒絕"""
    order_uuid = "order-uuid-2"
    update_data = {
        "note": "Updated note",
        "items": [{"item_uuid": "item-uuid-1", "quantity": 3}],
    }

    with patch("app.services.order_service.get_order_by_uuid") as mock_get:
        mock_order = MagicMock()
        mock_order.uuid = order_uuid
        mock_order.customer_uuid = "customer-uuid-123"  # 與token中的uuid匹配
        mock_order.status = OrderStatusEnum.COOKING.value  # 非pending
        mock_get.return_value = mock_order

        headers = {"Authorization": mock_customer_token}
        response = client.put(
            f"/orders/{order_uuid}", json=update_data, headers=headers
        )
        assert response.status_code == 403


def test_update_order_as_customer_others_order(client, mock_customer_token):
    """測試顧客更新他人的訂單 - 應該被拒絕"""
    order_uuid = "order-uuid-3"
    update_data = {
        "note": "Updated note",
        "items": [{"item_uuid": "item-uuid-1", "quantity": 3}],
    }

    with patch("app.services.order_service.get_order_by_uuid") as mock_get:
        mock_order = MagicMock()
        mock_order.uuid = order_uuid
        mock_order.customer_uuid = "other-customer-uuid"  # 不是token中的顧客
        mock_order.status = OrderStatusEnum.PENDING.value  # pending
        mock_get.return_value = mock_order

        headers = {"Authorization": mock_customer_token}
        response = client.put(
            f"/orders/{order_uuid}", json=update_data, headers=headers
        )
        assert response.status_code == 403


def test_get_orders_as_customer(client, mock_customer_token):
    """測試顧客查詢自己的訂單"""
    with patch("app.services.order_service.get_orders_by_customer") as mock_get:
        mock_orders = [
            MagicMock(
                uuid="order-uuid-1",
                customer_uuid="customer-uuid-123",
                status=OrderStatusEnum.PENDING.value,
                total_amount=300,
            )
        ]
        mock_get.return_value = mock_orders

        headers = {"Authorization": mock_customer_token}
        response = client.get("/orders/", headers=headers)
        assert response.status_code == 200


def test_get_orders_as_staff(client, admin_token):
    """測試員工查詢所有訂單"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    with patch(
        "app.utils.permission_checker.PermissionChecker.require_staff_with_permission"
    ) as mock_perm:
        mock_perm.return_value = None

        with patch("app.services.order_service.get_orders") as mock_get_all:
            mock_orders = [
                MagicMock(uuid="order-1", status=OrderStatusEnum.PENDING.value),
                MagicMock(uuid="order-2", status=OrderStatusEnum.COMPLETED.value),
            ]
            mock_get_all.return_value = mock_orders

            response = client.get("/orders/", headers=headers)
            assert response.status_code == 200


def test_update_order_status_as_staff(client, admin_token):
    """測試員工更新訂單狀態"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    order_uuid = "order-uuid-1"
    status_data = {"status": "COOKING"}

    with patch(
        "app.utils.permission_checker.PermissionChecker.require_staff_with_permission"
    ) as mock_perm:
        mock_perm.return_value = None

        with patch("app.services.order_service.update_order_status") as mock_update:
            mock_order = MagicMock()
            mock_order.uuid = order_uuid
            mock_order.status = OrderStatusEnum.COOKING.value
            mock_update.return_value = mock_order

            response = client.put(
                f"/orders/{order_uuid}/status", json=status_data, headers=headers
            )
            assert response.status_code == 200


def test_update_order_status_as_customer_forbidden(client, mock_customer_token):
    """測試顧客更新訂單狀態 - 應該被拒絕"""
    headers = {"Authorization": mock_customer_token}
    order_uuid = "order-uuid-1"
    status_data = {"status": "COOKING"}

    response = client.put(
        f"/orders/{order_uuid}/status", json=status_data, headers=headers
    )
    assert response.status_code == 403


def test_get_specific_order_as_customer_own(client, mock_customer_token):
    """測試顧客查詢自己的訂單詳情"""
    order_uuid = "order-uuid-1"

    with patch("app.services.order_service.get_order_by_uuid") as mock_get:
        mock_order = MagicMock()
        mock_order.uuid = order_uuid
        mock_order.customer_uuid = "customer-uuid-123"  # 與token中的uuid匹配
        mock_order.status = OrderStatusEnum.PENDING.value
        mock_get.return_value = mock_order

        headers = {"Authorization": mock_customer_token}
        response = client.get(f"/orders/{order_uuid}", headers=headers)
        assert response.status_code == 200


def test_get_specific_order_as_customer_others(client, mock_customer_token):
    """測試顧客查詢他人的訂單詳情 - 應該被拒絕"""
    order_uuid = "order-uuid-2"

    with patch("app.services.order_service.get_order_by_uuid") as mock_get:
        mock_order = MagicMock()
        mock_order.uuid = order_uuid
        mock_order.customer_uuid = "other-customer-uuid"  # 不是token中的顧客
        mock_order.status = OrderStatusEnum.PENDING.value
        mock_get.return_value = mock_order

        headers = {"Authorization": mock_customer_token}
        response = client.get(f"/orders/{order_uuid}", headers=headers)
        assert response.status_code == 403
