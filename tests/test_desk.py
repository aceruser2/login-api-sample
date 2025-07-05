import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app import app
from datetime import datetime

client = TestClient(app)


@pytest.fixture
def mock_desk_data():
    return {"desk_name": "Table 1"}


def test_create_desk(mock_desk_data, monkeypatch):
    """測試建立桌位"""

    def mock_create_desk(*args, **kwargs):
        return {
            "uuid": "desk-uuid-1",
            "desk_name": mock_desk_data["desk_name"],
            "soft_delete": False,
            "create_dt": datetime.now(),
            "update_dt": datetime.now(),
        }

    with patch("app.services.desk_service.create_desk", mock_create_desk):
        response = client.post("/desk/create", params=mock_desk_data)
        assert response.status_code == 200
        assert response.json()["uuid"] == "desk-uuid-1"
        assert response.json()["desk_name"] == mock_desk_data["desk_name"]


def test_get_desk(monkeypatch):
    """測試查詢單一桌位"""

    def mock_get_desk(*args, **kwargs):
        return {
            "uuid": "desk-uuid-1",
            "desk_name": "Table 1",
            "soft_delete": False,
            "create_dt": datetime.now().isoformat(),
            "update_dt": datetime.now().isoformat(),
        }

    with patch("app.services.desk_service.get_desk_by_uuid", mock_get_desk):
        response = client.get("/desk/desk-uuid-1")
        assert response.status_code == 200
        assert response.json()["uuid"] == "desk-uuid-1"


def test_list_desks(monkeypatch):
    """測試列出所有桌位"""

    def mock_get_all_desks(*args, **kwargs):
        return {
            "total": 2,
            "skip": 0,
            "limit": 10,
            "desks": [
                {
                    "uuid": "desk-uuid-1",
                    "desk_name": "Table 1",
                    "soft_delete": False,
                    "create_dt": datetime.now().isoformat(),
                    "update_dt": datetime.now().isoformat(),
                },
                {
                    "uuid": "desk-uuid-2",
                    "desk_name": "Table 2",
                    "soft_delete": False,
                    "create_dt": datetime.now().isoformat(),
                    "update_dt": datetime.now().isoformat(),
                },
            ],
        }

    with patch("app.services.desk_service.get_all_desks", mock_get_all_desks):
        response = client.get("/desks/")
        assert response.status_code == 200
        assert response.json()["total"] == 2
        assert len(response.json()["desks"]) == 2


def test_update_desk(monkeypatch):
    """測試更新桌位"""

    def mock_update_desk(*args, **kwargs):
        return {
            "uuid": "desk-uuid-1",
            "desk_name": "Updated Table",
            "soft_delete": False,
            "create_dt": datetime.now().isoformat(),
            "update_dt": datetime.now().isoformat(),
        }

    with patch("app.services.desk_service.update_desk", mock_update_desk):
        response = client.put(
            "/desk/update/desk-uuid-1", params={"desk_name": "Updated Table"}
        )
        assert response.status_code == 200
        assert response.json()["desk_name"] == "Updated Table"


def test_delete_desk(monkeypatch):
    """測試刪除桌位"""

    def mock_delete_desk(*args, **kwargs):
        return {
            "uuid": "desk-uuid-1",
            "desk_name": "Table 1",
            "soft_delete": True,
            "create_dt": datetime.now().isoformat(),
            "update_dt": datetime.now().isoformat(),
        }

    with patch("app.services.desk_service.delete_desk", mock_delete_desk):
        response = client.delete("/desk/delete/desk-uuid-1")
        assert response.status_code == 200
        assert response.json()["soft_delete"] == True
