import pytest
from .mock_test_api import client, admin_token, mock_user_data


def test_create_user(mock_user_data, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.post("/create_user/", json=mock_user_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == mock_user_data["username"]


def test_create_user_missing_required_fields(admin_token):
    """Test creating user with missing required fields"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    incomplete_data = {"username": "testuser"}
    response = client.post("/create_user/", json=incomplete_data, headers=headers)
    assert response.status_code == 400


def test_create_user_duplicate_email(mock_user_data, admin_token):
    """Test creating user with duplicate email"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Create first user
    client.post("/create_user/", json=mock_user_data, headers=headers)
    # Try creating second user with same email
    response = client.post("/create_user/", json=mock_user_data, headers=headers)
    assert response.status_code == 400


def test_create_user_invalid_role(mock_user_data, admin_token):
    """Test creating user with invalid role UUID"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    mock_user_data["role_uuid"] = "invalid-uuid"
    response = client.post("/create_user/", json=mock_user_data, headers=headers)
    assert response.status_code == 404


def test_get_user_by_uuid(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    user_uuid = "test-user-uuid"
    response = client.get(f"/get_user_by_uuid/?user_uuid={user_uuid}", headers=headers)
    assert response.status_code == 200
    assert response.json()["uuid"] == user_uuid


def test_delete_user(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    user_uuid = "test-user-uuid"
    response = client.delete(f"/delete_user/?user_uuid={user_uuid}", headers=headers)
    assert response.status_code == 200
    assert response.json()["uuid"] == user_uuid
