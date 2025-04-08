import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from fastapi import HTTPException

from app.adapter.model import Customer, Desk, DeskCustomer

log = logging.getLogger(__name__)


def create_customer(db: Session, customer_name: str, customer_phone: str):
    """Create a new customer if not exists"""
    try:
        existing_customer = db.execute(
            select(Customer).where(
                Customer.customer_phone == customer_phone, Customer.soft_delete == False
            )
        ).scalar()

        if existing_customer:
            return existing_customer

        new_customer = Customer(
            customer_name=customer_name, customer_phone=customer_phone
        )
        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)
        return new_customer
    except Exception as e:
        db.rollback()
        log.error(e)
        raise HTTPException(status_code=400, detail="create customer error")


def get_customer_by_phone(db: Session, customer_phone: str):
    try:
        customer = db.execute(
            select(Customer).where(
                Customer.customer_phone == customer_phone, Customer.soft_delete == False
            )
        ).scalar()
        if not customer:
            raise HTTPException(status_code=404, detail="customer not found")
        return customer
    except Exception as e:
        db.rollback()
        log.error(e)
        raise HTTPException(status_code=400, detail="get customer error")


def get_customer_by_uuid(db: Session, customer_uuid: str):
    try:
        customer = db.execute(
            select(Customer).where(
                Customer.uuid == customer_uuid, Customer.soft_delete == False
            )
        ).scalar()
        if not customer:
            raise HTTPException(status_code=404, detail="customer not found")
        return customer
    except Exception as e:
        db.rollback()
        log.error(e)
        raise HTTPException(status_code=400, detail="get customer error")


def create_desk_customer(db: Session, desk_uuid: str, customer_uuid: str):
    """內用登入，綁定桌子（1 小時有效）"""
    try:
        # 先確認此客戶有沒有活躍中的綁定（1 小時內）
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        active_binding = db.execute(
            select(DeskCustomer).where(
                DeskCustomer.customer_uuid == customer_uuid,
                DeskCustomer.soft_delete == False,
                DeskCustomer.create_dt >= one_hour_ago,
            )
        ).scalar()

        if active_binding:
            raise HTTPException(status_code=400, detail="Already assigned to a desk")

        new_binding = DeskCustomer(
            desk_uuid=desk_uuid,
            customer_uuid=customer_uuid,
        )
        db.add(new_binding)
        db.commit()
        db.refresh(new_binding)
        return new_binding
    except Exception as e:
        db.rollback()
        log.error(e)
        raise HTTPException(status_code=400, detail="create desk customer error")


def get_active_desk_customer(db: Session, customer_phone: str):
    """取得活躍中的內用綁定"""
    try:
        customer = get_customer_by_phone(db, customer_phone)

        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        desk_customer = db.execute(
            select(DeskCustomer).where(
                DeskCustomer.customer_uuid == customer.uuid,
                DeskCustomer.soft_delete == False,
                DeskCustomer.create_dt >= one_hour_ago,
            )
        ).scalar()

        if not desk_customer:
            raise HTTPException(status_code=404, detail="No active desk binding found")

        return desk_customer
    except Exception as e:
        db.rollback()
        log.error(e)
        raise HTTPException(status_code=400, detail="get desk-customer error")


def release_desk_binding(db: Session, customer_uuid: str):
    """結帳或自動解除綁定"""
    try:
        desk_customer = db.execute(
            select(DeskCustomer).where(
                DeskCustomer.customer_uuid == customer_uuid,
                DeskCustomer.soft_delete == False,
            )
        ).scalar()

        if not desk_customer:
            raise HTTPException(status_code=404, detail="no active desk binding")

        desk_customer.soft_delete = True
        db.commit()
        return {"message": "desk unbound"}
    except Exception as e:
        db.rollback()
        log.error(e)
        raise HTTPException(status_code=400, detail="release desk binding error")


def update_customer(
    db: Session,
    customer_uuid: str,
    customer_name: str = None,
    customer_phone: str = None,
):
    try:
        customer_data = get_customer_by_uuid(db, customer_uuid)
        if customer_name:
            customer_data.customer_name = customer_name
        if customer_phone:
            customer_data.customer_phone = customer_phone
        db.commit()
        db.refresh(customer_data)
        return customer_data
    except Exception as e:
        db.rollback()
        log.error(e)
        raise HTTPException(status_code=400, detail="update customer error")


def delete_customer(db: Session, customer_uuid: str):
    try:
        customer_data = get_customer_by_uuid(db, customer_uuid)
        customer_data.soft_delete = True
        db.commit()
        db.refresh(customer_data)
        return customer_data
    except Exception as e:
        db.rollback()
        log.error(e)
        raise HTTPException(status_code=400, detail="delete customer error")


def bind_desk_to_customer(db: Session, customer_phone: str, desk_uuid: str):
    """Bind a desk to a customer for dine-in"""
    try:
        customer = get_customer_by_phone(db, customer_phone)
        return create_desk_customer(db, desk_uuid, customer.uuid)
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=400, detail="bind desk to customer error")


def get_active_binding(db: Session, customer_phone: str):
    """Retrieve active desk binding for a customer"""
    try:
        return get_active_desk_customer(db, customer_phone)
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=400, detail="get active binding error")


def release_binding(db: Session, customer_phone: str):
    """Release desk binding for a customer"""
    try:
        customer = get_customer_by_phone(db, customer_phone)
        return release_desk_binding(db, customer.uuid)
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=400, detail="release binding error")
