import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app import app
from app.extension.emun_setting import OrderStatusEnum

client = TestClient(app)


def test_customer_cannot_access_staff_endpoints(client, mock_customer_token):
    """測試顧客無法訪問員工專用端點"""
    headers = {"Authorization": mock_customer_token}

    # 測試用戶管理端點
    response = client.get("/users/abc-123", headers=headers)
    assert response.status_code == 403

    # 測試創建桌位
    desk_data = {"desk_name": "Unauthorized Table"}
    response = client.post("/desks/", json=desk_data, headers=headers)
    assert response.status_code == 403

    # 測試支付管理
    payment_data = {"order_uuid": "test", "payment_method": "cash", "amount_paid": 100}
    response = client.post("/payments/", json=payment_data, headers=headers)
    assert response.status_code == 403

    # 測試報表查看
    response = client.get("/reports/daily-sales", headers=headers)
    assert response.status_code == 403


def test_unauthenticated_access_forbidden(client):
    """測試未認證用戶無法訪問受保護端點"""
    # 訂單管理
    response = client.get("/orders/")
    assert response.status_code == 401

    # 支付管理
    response = client.get("/payments/")
    assert response.status_code == 401

    # 用戶管理
    response = client.get("/users/me")
    assert response.status_code == 401

    # 報表查看
    response = client.get("/reports/daily-sales")
    assert response.status_code == 401


def test_staff_with_permission_can_access(client, admin_token):
    """測試有權限的員工可以訪問"""
    headers = {"Authorization": f"Bearer {admin_token}"}

    with patch(
        "app.utils.permission_checker.PermissionChecker.require_staff_with_permission"
    ) as mock_perm:
        mock_perm.return_value = None

        # 測試訂單管理
        with patch("app.services.order_service.get_orders") as mock_orders:
            mock_orders.return_value = []
            response = client.get("/orders/", headers=headers)
            assert response.status_code == 200

        # 測試菜單管理
        menu_data = {"name": "New Item", "price": 100, "category": "main"}
        with patch("app.services.menu_service.create_menu_item") as mock_create:
            mock_item = MagicMock()
            mock_item.uuid = "menu-uuid-1"
            mock_item.name = menu_data["name"]
            mock_create.return_value = mock_item

            response = client.post("/menu/items/", json=menu_data, headers=headers)
            assert response.status_code in [200, 201]


def test_staff_without_permission_cannot_access(client, admin_token):
    """測試無權限的員工無法訪問"""
    headers = {"Authorization": f"Bearer {admin_token}"}

    with patch(
        "app.utils.permission_checker.PermissionChecker.require_staff_with_permission"
    ) as mock_perm:
        from fastapi import HTTPException

        mock_perm.side_effect = HTTPException(
            status_code=403, detail="Permission denied"
        )

        # 測試報表查看
        response = client.get("/reports/daily-sales", headers=headers)
        assert response.status_code == 403

        # 測試支付管理
        payment_data = {
            "order_uuid": "test",
            "payment_method": "cash",
            "amount_paid": 100,
        }
        response = client.post("/payments/", json=payment_data, headers=headers)
        assert response.status_code == 403


def test_customer_order_lifecycle_permissions(client, mock_customer_token):
    """測試顧客在訂單生命週期中的權限"""
    headers = {"Authorization": mock_customer_token}
    customer_uuid = "customer-uuid-123"  # 假設與token中的UUID匹配

    # 1. 創建訂單 - 允許
    order_data = {
        "customer_uuid": customer_uuid,
        "desk_uuid": "desk-uuid-1",
        "order_type": "dine-in",
        "items": [{"item_uuid": "item-uuid-1", "quantity": 2}],
    }

    with patch("app.services.order_service.create_order") as mock_create:
        mock_order = MagicMock()
        mock_order.uuid = "order-uuid-1"
        mock_order.customer_uuid = customer_uuid
        mock_order.status = OrderStatusEnum.PENDING.value
        mock_create.return_value = mock_order

        response = client.post("/orders/", json=order_data, headers=headers)
        assert response.status_code in [200, 201]

        order_uuid = mock_order.uuid

    # 2. 更新pending訂單 - 允許
    update_data = {"note": "Updated note"}

    with patch("app.services.order_service.get_order_by_uuid") as mock_get:
        mock_get.return_value = mock_order

        with patch("app.services.order_service.update_order") as mock_update:
            mock_update.return_value = mock_order

            response = client.put(
                f"/orders/{order_uuid}", json=update_data, headers=headers
            )
            assert response.status_code == 200

    # 3. 更新訂單狀態 - 拒絕
    status_data = {"status": "COOKING"}
    response = client.put(
        f"/orders/{order_uuid}/status", json=status_data, headers=headers
    )
    assert response.status_code == 403

    # 4. 更新非pending訂單 - 拒絕
    with patch("app.services.order_service.get_order_by_uuid") as mock_get:
        mock_order.status = OrderStatusEnum.COOKING.value  # 已經不是pending狀態
        mock_get.return_value = mock_order

        response = client.put(
            f"/orders/{order_uuid}", json=update_data, headers=headers
        )
        assert response.status_code == 403


def test_public_endpoints_accessible(client):
    """測試公開端點可訪問"""
    # 測試菜單列表
    with patch("app.services.menu_service.get_menu_items") as mock_get:
        mock_get.return_value = []
        response = client.get("/menu/items/")
        assert response.status_code == 200

    # 測試桌位列表
    with patch("app.services.desk_service.get_all_desks") as mock_get:
        mock_get.return_value = []
        response = client.get("/desks/")
        assert response.status_code == 200
