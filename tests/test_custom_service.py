import pytest
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock, create_autospec
from datetime import datetime, timedelta, timezone
from app.services.custom_service import (
    create_customer,
    get_customer_by_email,
    bind_desk_to_customer,
    get_active_binding,
    release_binding,
)
from app.model import Customer, DeskCustomer


@pytest.fixture
def mock_db():
    return create_autospec(Session)


def test_create_customer_new(mock_db):
    """測試建立新顧客"""
    # 模擬資料庫查詢無結果
    mock_db.execute.return_value.scalar.return_value = None

    # 模擬創建新顧客
    mock_customer = MagicMock()
    mock_customer.uuid = "new-customer-uuid"
    mock_db.add.return_value = None

    # 調用待測試函數
    customer_data = {
        "customer_name": "New Customer",
        "customer_phone": "1234567890",
        "email": "new@example.com",
        "is_verified": False,
    }

    # 設置顧客物件屬性
    def side_effect(*args, **kwargs):
        mock_customer.customer_name = customer_data["customer_name"]
        mock_customer.customer_phone = customer_data["customer_phone"]
        mock_customer.email = customer_data["email"]
        mock_customer.is_verified = customer_data["is_verified"]

    # 替換 Customer 類的建構函數
    with patch("app.model.Customer", return_value=mock_customer) as mock_customer_class:
        mock_customer_class.side_effect = side_effect

        result = create_customer(
            db=mock_db,
            customer_name=customer_data["customer_name"],
            customer_phone=customer_data["customer_phone"],
            email=customer_data["email"],
            is_verified=customer_data["is_verified"],
        )

        # 驗證結果
        assert result.uuid == "new-customer-uuid"
        assert mock_db.add.called
        assert mock_db.flush.called


def test_create_customer_existing(mock_db):
    """測試使用現有顧客信箱"""
    # 模擬資料庫查詢有結果
    mock_existing_customer = MagicMock()
    mock_existing_customer.uuid = "existing-uuid"
    mock_existing_customer.customer_phone = "1234567890"
    mock_existing_customer.email = "existing@example.com"

    mock_db.execute.return_value.scalar.return_value = mock_existing_customer

    # 調用待測試函數
    result = create_customer(
        db=mock_db,
        customer_name="Existing Customer",
        customer_phone="1234567890",
        email="existing@example.com",
        is_verified=True,
    )

    # 驗證結果 - 應該返回現有顧客
    assert result.uuid == "existing-uuid"
    assert not mock_db.add.called  # 不應該添加新記錄
    assert not mock_db.flush.called  # 不應該進行數據庫操作


def test_get_customer_by_email(mock_db):
    """測試通過電子郵件獲取顧客"""
    mock_customer = MagicMock()
    mock_customer.uuid = "customer-uuid"
    mock_db.execute.return_value.scalar.return_value = mock_customer

    result = get_customer_by_email(mock_db, "test@example.com")

    assert result.uuid == "customer-uuid"
    assert mock_db.execute.called


def test_bind_desk_to_customer(mock_db):
    """測試綁定顧客到桌位"""
    # 模擬顧客查詢結果
    mock_customer = MagicMock()
    mock_customer.uuid = "customer-uuid"

    # 模擬綁定查詢結果
    mock_binding = MagicMock()
    mock_binding.desk_uuid = "desk-uuid"
    mock_binding.customer_uuid = "customer-uuid"

    # 設置 get_customer_by_email 的 Mock
    with patch(
        "app.services.custom_service.get_customer_by_email", return_value=mock_customer
    ), patch(
        "app.services.custom_service.create_desk_customer", return_value=mock_binding
    ):

        result = bind_desk_to_customer(mock_db, "test@example.com", "desk-uuid")

        assert result.desk_uuid == "desk-uuid"
        assert result.customer_uuid == "customer-uuid"


def test_get_active_binding(mock_db):
    """測試獲取活躍綁定"""
    # 模擬顧客查詢結果
    mock_customer = MagicMock()
    mock_customer.uuid = "customer-uuid"

    # 模擬活躍綁定
    mock_binding = MagicMock()
    mock_binding.desk_uuid = "desk-uuid"
    mock_binding.customer_uuid = "customer-uuid"
    mock_binding.create_dt = datetime.now(timezone.utc) - timedelta(
        minutes=30
    )  # 30分鐘前創建的綁定

    # 設置 Mock
    with patch(
        "app.services.custom_service.get_customer_by_email", return_value=mock_customer
    ), patch(
        "app.services.custom_service.get_active_desk_customer",
        return_value=mock_binding,
    ):

        result = get_active_binding(mock_db, "test@example.com")

        assert result.desk_uuid == "desk-uuid"
        assert result.customer_uuid == "customer-uuid"
