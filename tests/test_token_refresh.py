import pytest
from .mock_test_api import client, admin_token, db_session, setup_database


def test_refresh_token(setup_database, admin_token, db_session):
    """Test token refresh functionality"""
    # First login to get tokens

    assert "refresh_token" in admin_token
    refresh_token = admin_token["refresh_token"]

    # Try refreshing token
    headers = {"Authorization": f"bearer {refresh_token}"}
    response = client.post("/refresh/staff", headers=headers)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_refresh_token_invalid():
    """Test refresh with invalid token"""
    headers = {"Authorization": "Bearer invalid-token"}
    response = client.post("/refresh/staff", headers=headers)
    assert response.status_code == 401
