import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.model import Customer, Desk, DeskCustomer

log = logging.getLogger(__name__)


def create_customer(
    db: Session, customer_name: str, customer_phone: str, email: str, is_verified: bool
):
    """
    創建新顧客或獲取已存在的顧客
    """
    stmt = select(Customer).where(
        Customer.email == email,
        Customer.soft_delete == False,
    )
    existing_customer = db.execute(stmt).scalar_one_or_none()

    if existing_customer:
        if existing_customer.customer_phone != customer_phone:
            raise ValueError("此信箱已綁定其他手機號，請聯絡客服或用原手機號登入")
        return existing_customer

    # 檢查手機號是否已被其他帳號使用
    phone_stmt = select(Customer).where(
        Customer.customer_phone == customer_phone,
        Customer.soft_delete == False,
    )
    phone_customer = db.execute(phone_stmt).scalar_one_or_none()
    if phone_customer:
        if phone_customer.email != email:
            raise ValueError("此手機號已被其他帳號使用")

    new_customer = Customer(
        customer_name=customer_name,
        customer_phone=customer_phone,
        email=email,
        is_verified=is_verified,
    )
    db.add(new_customer)
    db.flush()
    return new_customer


def get_customer_by_email(db: Session, email: str):
    """
    通過電子郵件查詢顧客
    """
    stmt = select(Customer).where(
        Customer.email == email, Customer.soft_delete == False
    )
    return db.execute(stmt).scalar_one_or_none()


def get_customer_by_uuid(db: Session, customer_uuid: str):
    """
    通過UUID查詢顧客
    """
    stmt = select(Customer).where(
        Customer.uuid == customer_uuid, Customer.soft_delete == False
    )
    customer = db.execute(stmt).scalar_one_or_none()
    if not customer:
        raise ValueError("customer not found")
    return customer


def create_desk_customer(db: Session, desk_uuid: str, customer_uuid: str):
    """
    內用顧客綁定桌位（1小時內有效）
    """
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    stmt = select(DeskCustomer).where(
        DeskCustomer.customer_uuid == customer_uuid,
        DeskCustomer.soft_delete == False,
        DeskCustomer.create_dt >= one_hour_ago,
    )
    active_binding = db.execute(stmt).scalar_one_or_none()

    if active_binding:
        raise ValueError("Already assigned to a desk")

    new_binding = DeskCustomer(
        desk_uuid=desk_uuid,
        customer_uuid=customer_uuid,
    )
    db.add(new_binding)
    db.flush()
    return new_binding


def get_active_desk_customer(db: Session, customer_email: str):
    """
    查詢顧客目前有效的桌位綁定（1小時內）
    """
    customer = get_customer_by_email(db, customer_email)
    if not customer:
        raise ValueError("Customer not found")

    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    stmt = select(DeskCustomer).where(
        DeskCustomer.customer_uuid == customer.uuid,
        DeskCustomer.soft_delete == False,
        DeskCustomer.create_dt >= one_hour_ago,
    )
    desk_customer = db.execute(stmt).scalar_one_or_none()

    if not desk_customer:
        raise ValueError("No active desk binding found")

    return desk_customer


def release_desk_binding(db: Session, customer_uuid: str):
    """
    釋放顧客的桌位綁定（結帳時調用）
    """
    stmt = select(DeskCustomer).where(
        DeskCustomer.customer_uuid == customer_uuid,
        DeskCustomer.soft_delete == False,
    )
    desk_customer = db.execute(stmt).scalar_one_or_none()

    if not desk_customer:
        raise ValueError("no active desk binding")

    desk_customer.soft_delete = True
    return {"message": "desk unbound"}


def update_customer(
    db: Session,
    customer_uuid: str,
    customer_name: str = None,
    customer_phone: str = None,
):
    """
    更新顧客資訊

    Args:
        db (Session): 資料庫連線
        customer_uuid (str): 顧客UUID
        customer_name (str, optional): 顧客姓名
        customer_phone (str, optional): 顧客電話

    Returns:
        Customer: 更新後的顧客
    """
    customer_data = get_customer_by_uuid(db, customer_uuid)
    if customer_name:
        customer_data.customer_name = customer_name
    if customer_phone:
        customer_data.customer_phone = customer_phone
    return customer_data


def delete_customer(db: Session, customer_uuid: str):
    """
    刪除顧客（軟刪除）

    Args:
        db (Session): 資料庫連線
        customer_uuid (str): 顧客UUID

    Returns:
        Customer: 被刪除的顧客
    """
    customer_data = get_customer_by_uuid(db, customer_uuid)
    customer_data.soft_delete = True
    return customer_data


def bind_desk_to_customer(db: Session, customer_email: str, desk_uuid: str):
    """
    內用顧客綁定桌位的高階函數

    Args:
        db (Session): 資料庫連線
        customer_email (str): 顧客電子郵件
        desk_uuid (str): 桌位UUID

    Returns:
        DeskCustomer: 成功建立的桌位綁定
    """
    customer = get_customer_by_email(db, customer_email)
    return create_desk_customer(db, desk_uuid, customer.uuid)


def get_active_binding(db: Session, customer_email: str):
    """
    獲取顧客活躍的桌位綁定的高階函數

    Args:
        db (Session): 資料庫連線
        customer_email (str): 顧客電子郵件

    Returns:
        DeskCustomer: 活躍的桌位綁定
    """
    return get_active_desk_customer(db, customer_email)


def release_binding(db: Session, customer_email: str):
    """
    釋放顧客桌位綁定的高階函數

    Args:
        db (Session): 資料庫連線
        customer_email (str): 顧客電子郵件

    Returns:
        dict: 包含釋放結果訊息的字典
    """
    customer = get_customer_by_email(db, customer_email)
    return release_desk_binding(db, customer.uuid)
