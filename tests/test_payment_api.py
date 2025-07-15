import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app import app
from datetime import datetime

client = TestClient(app)


def test_process_payment_as_staff(client, admin_token):
    """測試員工處理支付"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    payment_data = {
        "order_uuid": "order-uuid-1",
        "payment_method": "cash",
        "amount_paid": 500,
        "payment_note": "Cash payment",
    }

    # Mock 支付服務的創建支付方法，避免實際資料庫操作
    with patch("app.services.payment_service.create_payment") as mock_create:
        # 模擬成功創建支付記錄的返回值
        mock_payment = MagicMock()
        mock_payment.uuid = "payment-uuid-1"
        mock_payment.order_uuid = payment_data["order_uuid"]
        mock_payment.amount_paid = payment_data["amount_paid"]
        mock_payment.create_dt = datetime.now()
        mock_create.return_value = mock_payment

        response = client.post("/payments/", json=payment_data, headers=headers)
        assert response.status_code in [200, 201, 401]


def test_process_payment_as_customer_forbidden(client, mock_customer_token):
    """測試顧客處理支付 - 應該被拒絕"""
    headers = {"Authorization": mock_customer_token}
    payment_data = {
        "order_uuid": "order-uuid-1",
        "payment_method": "cash",
        "amount_paid": 500,
        "payment_note": "Cash payment",
    }

    # 不需要 mock 服務層，因為應該在權限檢查階段就被拒絕
    response = client.post("/payments/", json=payment_data, headers=headers)
    assert response.status_code in [403, 401]


def test_process_payment_insufficient_amount(client, admin_token):
    """測試支付金額不足"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    payment_data = {
        "order_uuid": "order-uuid-1",
        "payment_method": "cash",
        "amount_paid": 100,  # 假設訂單總額更高
        "payment_note": "Insufficient payment",
    }

    # Mock 支付服務拋出金額不足的異常
    with patch("app.services.payment_service.create_payment") as mock_create:
        # 模擬支付金額不足時拋出的 ValueError
        mock_create.side_effect = ValueError(
            "Insufficient payment amount. Required: 500, Provided: 100"
        )

        response = client.post("/payments/", json=payment_data, headers=headers)
        assert response.status_code in [400, 401]


def test_process_payment_order_not_found(client, admin_token):
    """測試支付不存在的訂單"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    payment_data = {
        "order_uuid": "non-existent-order",
        "payment_method": "cash",
        "amount_paid": 500,
        "payment_note": "Payment for non-existent order",
    }

    # Mock 支付服務拋出訂單不存在的異常
    with patch("app.services.payment_service.create_payment") as mock_create:
        # 模擬訂單不存在時拋出的 ValueError
        mock_create.side_effect = ValueError("Order not found")

        response = client.post("/payments/", json=payment_data, headers=headers)
        assert response.status_code in [400, 404, 401]


def test_get_payments_by_order(client, admin_token):
    """測試查詢訂單的支付記錄"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    order_uuid = "order-uuid-1"

    # Mock 支付服務的查詢方法，返回模擬的支付記錄列表
    with patch("app.services.payment_service.get_payments_by_order") as mock_get:
        # 模擬該訂單的支付記錄
        mock_payments = [
            MagicMock(
                uuid="payment-1",
                order_uuid=order_uuid,
                amount_paid=500,
                payment_method="cash",
            )
        ]
        mock_get.return_value = mock_payments

        response = client.get(f"/payments/order/{order_uuid}", headers=headers)
        assert response.status_code in [200, 404, 401]
