import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app import app

client = TestClient(app)


def test_staff_login_success(client,admin_token):
    """測試員工登入成功"""
    # 使用 conftest 中已創建的 admin 帳號
    login_data = {"username": "admin", "password": "123456"}
    response = client.post("/token/staff", json=login_data)

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_staff_login_invalid_credentials(client):
    """測試員工登入失敗 - 密碼錯誤"""
    login_data = {"username": "admin", "password": "wrongpassword"}
    response = client.post("/token/staff", json=login_data)

    assert response.status_code == 401


def test_staff_login_user_not_found(client):
    """測試員工登入失敗 - 使用者不存在"""
    login_data = {"username": "nonexistent", "password": "123456"}
    response = client.post("/token/staff", json=login_data)

    assert response.status_code == 401


def test_staff_login_missing_fields(client):
    """測試員工登入失敗 - 缺少必要欄位"""
    login_data = {"username": "admin"}  # 缺少密碼
    response = client.post("/token/staff", json=login_data)

    assert response.status_code == 422  # FastAPI/Pydantic 會回傳 422


def test_staff_refresh_token(client, refresh_token):
    """測試員工刷新 token"""
    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = client.post("/refresh/staff", headers=headers)

    assert response.status_code in [200]  # 可能因為 refresh endpoint 未實現
