import logging
from sqlalchemy.orm import Session
from sqlalchemy import select
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


def create_desk_customer(db: Session, desk_uuid: str, customer_uuid: str):
    """Associate a customer with a desk"""
    try:
        new_desk_customer = DeskCustomer(
            desk_uuid=desk_uuid, customer_uuid=customer_uuid
        )
        db.add(new_desk_customer)
        db.commit()
        db.refresh(new_desk_customer)
        return new_desk_customer
    except Exception as e:
        db.rollback()
        log.error(e)
        raise HTTPException(status_code=400, detail="create desk customer error")

def get_desk_customer(db: Session, customer_phone: str,on_time):
    """"""
    try:
        select(Customer).join(DeskCustomer,DeskCustomer.).where(
                DeskCustomer.soft_delete == False,
            )
        desk_customer_data = db.execute(
            
        ).scalar()
        if not desk_customer_data:
            raise HTTPException(status_code=404, detail="desk-customer not found")
        return desk_customer_data
    except Exception as e:
        db.rollback()
        log.error(e)
        raise HTTPException(status_code=400, detail="get desk-customer error")


def get_customer_by_phone(db: Session, customer_phone: str):
    """Retrieve customer by phone number"""
    try:
        customer_data = db.execute(
            select(customer).where(
                customer.customer_phone == customer_phone, customer.soft_delete == False
            )
        ).scalar()
        if not customer_data:
            raise HTTPException(status_code=404, detail="customer not found")
        return customer_data
    except Exception as e:
        db.rollback()
        log.error(e)
        raise HTTPException(status_code=400, detail="get customer error")


def get_customer_by_uuid(db: Session, customer_uuid: str):
    """Retrieve customer by UUID"""
    try:
        customer_data = db.execute(
            select(customer).where(
                customer.uuid == customer_uuid, customer.soft_delete == False
            )
        ).scalar()
        if not customer_data:
            raise HTTPException(status_code=404, detail="customer not found")
        return customer_data
    except Exception as e:
        db.rollback()
        log.error(e)
        raise HTTPException(status_code=400, detail="get customer error")


def update_customer(
    db: Session,
    customer_uuid: str,
    customer_name: str = None,
    customer_phone: str = None,
):
    """Update customer details"""
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
    """Soft delete a customer"""
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
