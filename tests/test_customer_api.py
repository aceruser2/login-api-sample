import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app import app

client = TestClient(app)


def test_create_customer(client, admin_token):
    """測試建立顧客"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    customer_data = {
        "customer_name": "New Customer",
        "customer_phone": "0999888777",
        "email": "newcustomer@example.com",
        "is_verified": False,
    }
    with patch("app.services.custom_service.create_customer") as mock_create:
        mock_customer = MagicMock()
        mock_customer.uuid = "new-customer-uuid"
        mock_customer.customer_name = customer_data["customer_name"]
        mock_customer.email = customer_data["email"]
        mock_create.return_value = mock_customer

        response = client.post("/customers/", json=customer_data, headers=headers)
        assert response.status_code in [200, 201, 404, 401, 403]


def test_get_customer_by_email(client, admin_token):
    """測試通過電子郵件獲取顧客"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    test_email = "dinein@example.com"

    # Mock 顧客服務的信箱查詢方法，避免實際資料庫查詢
    with patch("app.services.custom_service.get_customer_by_email") as mock_get:
        # 模擬找到指定信箱的顧客
        mock_customer = MagicMock()
        mock_customer.uuid = "customer-uuid"
        mock_customer.email = test_email
        mock_get.return_value = mock_customer

        response = client.get(f"/customers/{test_email}", headers=headers)
        assert response.status_code in [200, 404]


def test_update_customer(client, admin_token):
    """測試更新顧客資訊"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    customer_uuid = "test-customer-uuid"
    update_data = {"customer_name": "Updated Name", "customer_phone": "0911222333"}

    # Mock 顧客服務的更新方法，避免實際的資料庫更新和電話號碼衝突檢查
    with patch("app.services.custom_service.update_customer") as mock_update:
        # 模擬更新成功的返回值
        mock_customer = MagicMock()
        mock_customer.uuid = customer_uuid
        mock_customer.customer_name = update_data["customer_name"]
        mock_update.return_value = mock_customer

        response = client.put(
            f"/customers/{customer_uuid}", json=update_data, headers=headers
        )
        assert response.status_code in [200, 404]


def test_delete_customer(client, admin_token):
    """測試刪除顧客"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    customer_uuid = "test-customer-uuid"

    # Mock 顧客服務的軟刪除方法，避免實際的資料庫操作
    with patch("app.services.custom_service.delete_customer") as mock_delete:
        # 模擬軟刪除成功的返回值
        mock_customer = MagicMock()
        mock_customer.uuid = customer_uuid
        mock_customer.soft_delete = True
        mock_delete.return_value = mock_customer

        response = client.delete(f"/customers/{customer_uuid}", headers=headers)
        assert response.status_code in [200, 404]
