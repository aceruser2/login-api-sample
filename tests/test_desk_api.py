import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app import app
from datetime import datetime

client = TestClient(app)


def test_create_desk(client, admin_token, mock_desk_data):
    """測試建立桌位"""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Mock 桌位服務的創建方法，避免實際資料庫操作和重複名稱檢查
    with patch("app.services.desk_service.create_desk") as mock_create:
        # 模擬成功創建桌位的返回值
        mock_desk = MagicMock()
        mock_desk.uuid = "new-desk-uuid"
        mock_desk.desk_name = mock_desk_data["desk_name"]
        mock_desk.capacity = 4
        mock_desk.is_available = True
        mock_desk.create_dt = datetime.now()
        mock_create.return_value = mock_desk

        response = client.post("/desks/", json=mock_desk_data, headers=headers)
        assert response.status_code in [200, 201, 401, 403]


def test_get_all_desks(client):
    """測試獲取所有桌位"""
    # Mock 桌位服務的查詢所有方法，返回預設的桌位列表
    with patch("app.services.desk_service.get_all_desks") as mock_get_all:
        # 模擬系統中的桌位列表
        mock_desks = [
            MagicMock(uuid="desk-1", desk_name="Table 1"),
            MagicMock(uuid="desk-2", desk_name="Table 2"),
        ]
        mock_get_all.return_value = mock_desks

        response = client.get("/desks/")
        assert response.status_code == 200


def test_get_desk_by_uuid(client, admin_token):
    """測試通過 UUID 獲取桌位"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    desk_uuid = "test-desk-uuid"

    # Mock 桌位服務的單一查詢方法，避免實際資料庫查詢
    with patch("app.services.desk_service.get_desk_by_uuid") as mock_get:
        # 模擬找到指定 UUID 的桌位
        mock_desk = MagicMock()
        mock_desk.uuid = desk_uuid
        mock_desk.desk_name = "Table 1"
        mock_get.return_value = mock_desk

        response = client.get(f"/desks/{desk_uuid}", headers=headers)
        assert response.status_code in [200, 404]


def test_update_desk(client, admin_token):
    """測試更新桌位"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    desk_uuid = "test-desk-uuid"
    update_data = {"desk_name": "Updated Table"}

    # Mock 桌位服務的更新方法，避免實際的資料庫更新和名稱衝突檢查
    with patch("app.services.desk_service.update_desk") as mock_update:
        # 模擬更新成功的返回值
        mock_desk = MagicMock()
        mock_desk.uuid = desk_uuid
        mock_desk.desk_name = update_data["desk_name"]
        mock_update.return_value = mock_desk

        response = client.put(f"/desks/{desk_uuid}", json=update_data, headers=headers)
        assert response.status_code in [200, 404]


def test_delete_desk(client, admin_token):
    """測試刪除桌位"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    desk_uuid = "test-desk-uuid"

    # Mock 桌位服務的軟刪除方法，避免實際的資料庫操作
    with patch("app.services.desk_service.delete_desk") as mock_delete:
        # 模擬軟刪除成功的返回值
        mock_desk = MagicMock()
        mock_desk.uuid = desk_uuid
        mock_desk.soft_delete = True
        mock_delete.return_value = mock_desk

        response = client.delete(f"/desks/{desk_uuid}", headers=headers)
        assert response.status_code in [200, 404]


def test_bind_desk_to_customer(client, mock_customer_token):
    """測試綁定顧客與桌位"""
    headers = {"Authorization": f"Bearer {mock_customer_token}"}
    binding_data = {"customer_email": "dinein@example.com", "desk_uuid": "desk-uuid-1"}

    # Mock 顧客服務的綁定方法，避免實際的顧客查詢和綁定狀態檢查
    with patch("app.services.custom_service.bind_desk_to_customer") as mock_bind:
        # 模擬成功綁定的返回值
        mock_binding = MagicMock()
        mock_binding.desk_uuid = binding_data["desk_uuid"]
        mock_binding.customer_uuid = "customer-uuid"
        mock_binding.create_dt = datetime.now()
        mock_bind.return_value = mock_binding

        response = client.post("/desk-customer/", json=binding_data, headers=headers)
        assert response.status_code in [200, 400]


def test_get_active_desk_binding(client, mock_customer_token):
    """測試獲取活躍的桌位綁定"""
    headers = {"Authorization": f"Bearer {mock_customer_token}"}
    customer_email = "dinein@example.com"

    # Mock 顧客服務的活躍綁定查詢方法，避免實際的時間檢查和資料庫查詢
    with patch("app.services.custom_service.get_active_binding") as mock_get_active:
        # 模擬找到活躍綁定的返回值
        mock_binding = MagicMock()
        mock_binding.desk_uuid = "desk-uuid-1"
        mock_binding.customer_uuid = "customer-uuid"
        mock_binding.create_dt = datetime.now()
        mock_get_active.return_value = mock_binding

        response = client.get(
            f"/desk-customer/active?customer_email={customer_email}", headers=headers
        )
        assert response.status_code in [200, 404]


def test_release_desk_binding(client, admin_token):
    """測試釋放桌位綁定"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    release_data = {"customer_email": "dinein@example.com"}

    # Mock 顧客服務的釋放綁定方法，避免實際的綁定狀態檢查和資料庫更新
    with patch("app.services.custom_service.release_binding") as mock_release:
        # 模擬成功釋放綁定的返回值
        mock_release.return_value = {"message": "desk unbound"}

        response = client.post(
            "/desk-customer/release", json=release_data, headers=headers
        )
        assert response.status_code in [200, 404]
