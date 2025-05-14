import pytest
from .mock_test_api import (
    client,
    mock_customer_data,
    admin_token,
    db_session,
    mock_menu_item,
    mock_order_data,
)


def test_payment_and_auto_release_desk(
    mock_customer_data, admin_token, db_session, mock_menu_item, mock_order_data
):
    """Test payment API and auto release desk binding after payment"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    # 1. 建立顧客與桌位綁定
    client.post(
        "/desk-customer/",
        json={
            "customer_phone": mock_customer_data["phone"],
            "desk_uuid": mock_customer_data["desk_uuid"],
        },
        headers=headers,
    )
    # 2. 建立訂單 (假設有 /order/create API)
    order_resp = client.post("/order/create", json=mock_order_data, headers=headers)
    assert order_resp.status_code == 200
    order_uuid = order_resp.json()["uuid"]
    total_amount = order_resp.json()["total_amount"]
    # 3. 支付
    payment_data = {
        "order_uuid": order_uuid,
        "payment_method": "cash",
        "amount_paid": total_amount,
        "payment_note": "test",
    }
    pay_resp = client.post("/payments/", json=payment_data, headers=headers)
    assert pay_resp.status_code == 200
    assert pay_resp.json()["order_uuid"] == order_uuid
    # 4. 檢查桌位綁定已自動解除
    resp = client.get(
        f"/desk-customer/active?customer_phone={mock_customer_data['phone']}",
        headers=headers,
    )
    assert resp.status_code == 404 or resp.json().get("desk_uuid") is None


def test_payment_insufficient_amount(
    mock_customer_data, admin_token, db_session, mock_menu_item, mock_order_data
):
    """Test payment API with insufficient amount"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    # 建立訂單
    order_resp = client.post("/order/create", json=mock_order_data, headers=headers)
    assert order_resp.status_code == 200
    order_uuid = order_resp.json()["uuid"]
    # 支付金額不足
    payment_data = {
        "order_uuid": order_uuid,
        "payment_method": "cash",
        "amount_paid": 50,
        "payment_note": "test",
    }
    pay_resp = client.post("/payments/", json=payment_data, headers=headers)
    assert pay_resp.status_code == 400


def test_daily_sales_report(admin_token):
    """Test daily sales report API"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.get("/reports/daily-sales", headers=headers)
    assert resp.status_code == 200
    assert "total_sales" in resp.json()
    assert "total_orders" in resp.json()


def test_popular_items_report(admin_token):
    """Test popular items report API"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.get("/reports/popular-items", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    # 每個 item 至少有 item_uuid, item_name, quantity_sold, total_sales
    if resp.json():
        item = resp.json()[0]
        assert "item_uuid" in item
        assert "item_name" in item
        assert "quantity_sold" in item
        assert "total_sales" in item
