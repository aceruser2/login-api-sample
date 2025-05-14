import pytest
from .mock_test_api import client, mock_customer_data


def test_create_customer(mock_customer_data):
    response = client.post("/token/dine-in", json=mock_customer_data)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_create_customer_missing_fields():
    """Test creating customer with missing fields"""
    incomplete_data = {"custom_name": "Test"}
    response = client.post("/token/dine-in", json=incomplete_data)
    assert response.status_code == 400


def test_create_customer_with_verification(mock_customer_data):
    """Test complete customer creation flow with verification"""
    # First step - request verification
    mock_customer_data["email"] = "test@example.com"
    response = client.post("/token/dine-in", json=mock_customer_data)
    assert response.status_code == 200
    assert response.json()["require_verification"] == True

    # Second step - verify code
    verification_data = {**mock_customer_data, "verification_code": "123456"}
    response = client.post("/verify/dine-in", json=verification_data)
    assert response.status_code == 400  # Should fail with invalid code
