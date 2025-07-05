import pytest
from .mock_test_api import client, admin_token


def test_create_menu_item(admin_token):
    """測試創建菜單項目"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    menu_data = {
        "name": "測試漢堡",
        "description": "美味的測試漢堡",
        "price": 120,
        "category": "主餐",
        "image_url": "https://example.com/burger.jpg",
    }
    response = client.post("/menu/items/", json=menu_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == menu_data["name"]


def test_get_menu_items_with_inventory(admin_token):
    """測試獲取帶庫存的菜單項目"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/menu/items-with-inventory/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_menu_items_by_category(admin_token):
    """測試按類別獲取菜單項目"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/menu/items/?category=主餐", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_menu_item(admin_token):
    """測試更新菜單項目"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    # 先創建一個菜單項目
    menu_data = {
        "name": "測試披薩",
        "description": "美味的測試披薩",
        "price": 200,
        "category": "主餐",
    }
    create_response = client.post("/menu/items/", json=menu_data, headers=headers)
    item_uuid = create_response.json()["uuid"]

    # 更新菜單項目
    update_data = {"name": "更新後的披薩", "price": 250}
    response = client.put(f"/menu/items/{item_uuid}", json=update_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]
    assert response.json()["price"] == update_data["price"]


def test_delete_menu_item(admin_token):
    """測試刪除菜單項目"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    # 先創建一個菜單項目
    menu_data = {
        "name": "測試湯品",
        "description": "美味的測試湯品",
        "price": 80,
        "category": "湯品",
    }
    create_response = client.post("/menu/items/", json=menu_data, headers=headers)
    item_uuid = create_response.json()["uuid"]

    # 刪除菜單項目
    response = client.delete(f"/menu/items/{item_uuid}", headers=headers)
    assert response.status_code == 200
