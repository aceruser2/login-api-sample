import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.model import Customer, Desk, DeskCustomer

log = logging.getLogger(__name__)


def create_customer(
    db: Session, customer_name: str, customer_phone: str, email: str, is_verified: bool
):
    """Create a new customer if not exists"""
    existing_customer = db.execute(
        select(Customer).where(
            Customer.email == email,
            Customer.soft_delete == False,
        )
    ).scalar()

    if existing_customer:
        # 若手機號不同，視為換號，建議提示或軟刪原資料,但手機還是得認證尚未實作
        if existing_customer.customer_phone != customer_phone:
            raise ValueError("此信箱已綁定其他手機號，請聯絡客服或用原手機號登入")
        return existing_customer

    # 檢查手機號是否已被其他帳號使用
    phone_customer = db.execute(
        select(Customer).where(
            Customer.customer_phone == customer_phone,
            Customer.soft_delete == False,
        )
    ).scalar()
    if phone_customer:
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
    customer = db.execute(
        select(Customer).where(Customer.email == email, Customer.soft_delete == False)
    ).scalar()
    if not customer:
        return None
    return customer


def get_customer_by_uuid(db: Session, customer_uuid: str):
    customer = db.execute(
        select(Customer).where(
            Customer.uuid == customer_uuid, Customer.soft_delete == False
        )
    ).scalar()
    if not customer:
        raise ValueError("customer not found")
    return customer


def create_desk_customer(db: Session, desk_uuid: str, customer_uuid: str):
    """內用登入，綁定桌子（1 小時有效）"""
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
    """取得活躍中的內用綁定"""
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
    """結帳或自動解除綁定"""
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
    customer_data = get_customer_by_uuid(db, customer_uuid)
    if customer_name:
        customer_data.customer_name = customer_name
    if customer_phone:
        customer_data.customer_phone = customer_phone
    return customer_data


def delete_customer(db: Session, customer_uuid: str):
    customer_data = get_customer_by_uuid(db, customer_uuid)
    customer_data.soft_delete = True
    return customer_data


def bind_desk_to_customer(db: Session, customer_email: str, desk_uuid: str):
    """Bind a desk to a customer for dine-in"""
    customer = get_customer_by_email(db, customer_email)
    return create_desk_customer(db, desk_uuid, customer.uuid)


def get_active_binding(db: Session, customer_email: str):
    """Retrieve active desk binding for a customer"""
    return get_active_desk_customer(db, customer_email)


def release_binding(db: Session, customer_email: str):
    """Release desk binding for a customer"""
    customer = get_customer_by_email(db, customer_email)
    return release_desk_binding(db, customer.uuid)
