import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_customer_cannot_access_staff_endpoints(client, mock_customer_token):
    """測試顧客無法訪問員工專用端點"""
    headers = {"Authorization": mock_customer_token}

    # 測試訪問用戶管理端點
    response = client.get("/users/me", headers=headers)
    assert response.status_code in [403, 401, 404]

    # 測試創建桌位
    desk_data = {"desk_name": "Unauthorized Table"}
    response = client.post("/desks/", json=desk_data, headers=headers)
    assert response.status_code in [403, 401]


def test_unauthenticated_access_forbidden(client):
    """測試未認證用戶無法訪問受保護端點"""
    # 不提供認證 header
    response = client.get("/orders/")
    assert response.status_code in [401, 403]

    response = client.get("/payments/")
    assert response.status_code in [401, 403]

    response = client.get("/users/")
    assert response.status_code in [401, 403]


def test_invalid_token_rejected(client):
    """測試無效 token 被拒絕"""
    headers = {"Authorization": "Bearer invalid-token"}

    response = client.get("/orders/", headers=headers)
    assert response.status_code == 401

    response = client.get("/desks/", headers=headers)
    assert response.status_code == 401


def test_customer_can_access_own_data_only(client, mock_customer_token):
    """測試顧客只能訪問自己的資料"""
    headers = {"Authorization": mock_customer_token}

    # 測試查詢自己的訂單（應該允許）
    response = client.get("/orders/", headers=headers)
    assert response.status_code in [200]  # 可能因為 API 未實現返回 401

    # 測試查詢他人的桌位綁定（應該被拒絕）
    response = client.get(
        "/desk-customer/active?customer_email=other@example.com", headers=headers
    )
    assert response.status_code in [403, 401, 404]
