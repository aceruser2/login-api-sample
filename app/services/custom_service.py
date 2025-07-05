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

    Args:
        db (Session): 資料庫連線
        customer_name (str): 顧客姓名
        customer_phone (str): 顧客電話
        email (str): 顧客電子郵件（主要識別鍵）
        is_verified (bool): 是否已驗證

    Returns:
        Customer: 新建或已存在的顧客

    Raises:
        ValueError: 當電子郵件已與其他電話綁定或電話已與其他電子郵件綁定時
    """
    existing_customer = db.execute(
        select(Customer).where(
            Customer.email == email,
            Customer.soft_delete == False,
        )
    ).scalar()

    if existing_customer:
        # 若電話不同，視為換號，建議提示或軟刪原資料,但電話還是得認證尚未實作
        if existing_customer.customer_phone != customer_phone:
            raise ValueError("此信箱已綁定其他手機號，請聯絡客服或用原手機號登入")
        return existing_customer

    # 檢查 email 是否已被其他帳號使用（已於上方判斷）
    # 檢查手機號是否已被其他帳號使用（可選，視需求保留）
    phone_customer = db.execute(
        select(Customer).where(
            Customer.customer_phone == customer_phone,
            Customer.soft_delete == False,
        )
    ).scalar()
    if phone_customer:
        # 若同手機但不同 email，仍可提示
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

    Args:
        db (Session): 資料庫連線
        email (str): 顧客電子郵件

    Returns:
        Customer: 查詢到的顧客，如未找到則返回None
    """
    customer = db.execute(
        select(Customer).where(Customer.email == email, Customer.soft_delete == False)
    ).scalar()
    if not customer:
        return None
    return customer


def get_customer_by_uuid(db: Session, customer_uuid: str):
    """
    通過UUID查詢顧客

    Args:
        db (Session): 資料庫連線
        customer_uuid (str): 顧客UUID

    Returns:
        Customer: 查詢到的顧客

    Raises:
        ValueError: 當找不到顧客時
    """
    customer = db.execute(
        select(Customer).where(
            Customer.uuid == customer_uuid, Customer.soft_delete == False
        )
    ).scalar()
    if not customer:
        raise ValueError("customer not found")
    return customer


def create_desk_customer(db: Session, desk_uuid: str, customer_uuid: str):
    """
    內用顧客綁定桌位（1小時內有效）

    Args:
        db (Session): 資料庫連線
        desk_uuid (str): 桌位UUID
        customer_uuid (str): 顧客UUID

    Returns:
        DeskCustomer: 成功建立的桌位綁定

    Raises:
        ValueError: 當顧客已有活躍的桌位綁定時
    """
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    active_binding = db.execute(
        select(DeskCustomer).where(
            DeskCustomer.customer_uuid == customer_uuid,
            DeskCustomer.soft_delete == False,
            DeskCustomer.create_dt >= one_hour_ago,
        )
    ).scalar()

    if active_binding:
        raise ValueError("Already assigned to a desk")

    new_binding = DeskCustomer(
        desk_uuid=desk_uuid,
        customer_uuid=customer_uuid,
    )
    db.add(new_binding)
    db.flush(new_binding)
    return new_binding


def get_active_desk_customer(db: Session, customer_email: str):
    """
    查詢顧客目前有效的桌位綁定（1小時內）

    Args:
        db (Session): 資料庫連線
        customer_email (str): 顧客電子郵件

    Returns:
        DeskCustomer: 有效的桌位綁定

    Raises:
        ValueError: 當找不到有效的桌位綁定時
    """
    customer = get_customer_by_email(db, customer_email)

    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    desk_customer = db.execute(
        select(DeskCustomer).where(
            DeskCustomer.customer_uuid == customer.uuid,
            DeskCustomer.soft_delete == False,
            DeskCustomer.create_dt >= one_hour_ago,
        )
    ).scalar()

    if not desk_customer:
        raise ValueError("No active desk binding found")

    return desk_customer


def release_desk_binding(db: Session, customer_uuid: str):
    """
    釋放顧客的桌位綁定（結帳時調用）

    Args:
        db (Session): 資料庫連線
        customer_uuid (str): 顧客UUID

    Returns:
        dict: 包含釋放結果訊息的字典

    Raises:
        ValueError: 當找不到活躍的桌位綁定時
    """
    desk_customer = db.execute(
        select(DeskCustomer).where(
            DeskCustomer.customer_uuid == customer_uuid,
            DeskCustomer.soft_delete == False,
        )
    ).scalar()

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
