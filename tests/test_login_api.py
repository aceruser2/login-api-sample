import pytest
from .mock_test_api import client, mock_user_data


def test_login_user(mock_user_data):
    login_data = {
        "username": mock_user_data["username"],
        "password": mock_user_data["password"],
        "userstatus": 0,
    }
    response = client.post("/token/user", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_credentials(mock_user_data):
    """Test login with invalid credentials"""
    login_data = {
        "username": mock_user_data["username"],
        "password": "wrongpassword",
        "userstatus": 0,
    }
    response = client.post("/token/user", json=login_data)
    assert response.status_code == 401


def test_login_missing_fields():
    """Test login with missing fields"""
    response = client.post("/token/user", json={})
    assert response.status_code == 400
