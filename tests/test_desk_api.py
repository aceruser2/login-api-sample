import pytest
from .mock_test_api import client, mock_customer_data, admin_token, mock_desk_data


def test_bind_desk(mock_customer_data, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    request_data = {
        "customer_phone": mock_customer_data["phone"],
        "desk_uuid": mock_customer_data["desk_uuid"],
    }
    response = client.post("/desk-customer/", json=request_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["desk_uuid"] == mock_customer_data["desk_uuid"]


def test_get_active_desk_binding(mock_customer_data, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    customer_phone = mock_customer_data["phone"]
    response = client.get(
        f"/desk-customer/active?customer_phone={customer_phone}", headers=headers
    )
    assert response.status_code == 200
    assert response.json()["desk_uuid"] == mock_customer_data["desk_uuid"]


def test_release_desk(mock_customer_data, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    request_data = {"customer_phone": mock_customer_data["phone"]}
    response = client.post("/desk-customer/release", json=request_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "desk unbound"


def test_create_desk(mock_desk_data, admin_token):
    """Test desk creation"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.post("/desk/create", json=mock_desk_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["desk_name"] == mock_desk_data["desk_name"]


def test_get_all_desks(admin_token):
    """Test retrieving all desks"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/desks/", headers=headers)
    assert response.status_code == 200
    assert "total" in response.json()
    assert "desks" in response.json()


def test_bind_desk_invalid_desk(mock_customer_data, admin_token):
    """Test binding with invalid desk UUID"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    request_data = {
        "customer_phone": mock_customer_data["phone"],
        "desk_uuid": "invalid-uuid",
    }
    response = client.post("/desk-customer/", json=request_data, headers=headers)
    assert response.status_code == 404


def test_bind_desk_already_bound(mock_customer_data, admin_token):
    """Test binding when customer already has active binding"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    request_data = {
        "customer_phone": mock_customer_data["phone"],
        "desk_uuid": mock_customer_data["desk_uuid"],
    }
    # First binding
    client.post("/desk-customer/", json=request_data, headers=headers)
    # Try second binding
    response = client.post("/desk-customer/", json=request_data, headers=headers)
    assert response.status_code == 400
