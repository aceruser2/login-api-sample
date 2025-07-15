from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from app.extension.sql_ext import get_session, Session
from app.services import custom_service
from app.schema.customer_schema import CustomerCreate, CustomerResponse, CustomerUpdate
from app.extension.jwt_config import get_current_user

router = APIRouter(prefix="/customers", tags=["customers"])
log = logging.getLogger(__name__)


@router.post("/", response_model=CustomerResponse)
def create_customer(customer_data: CustomerCreate, db: Session = Depends(get_session)):
    """創建新顧客"""
    try:
        customer = custom_service.create_customer(
            db=db,
            customer_name=customer_data.customer_name,
            customer_phone=customer_data.customer_phone,
            email=customer_data.email,
            is_verified=customer_data.is_verified,
        )
        db.commit()
        return customer
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{customer_email}", response_model=CustomerResponse)
def get_customer(customer_email: str, db: Session = Depends(get_session)):
    """通過電子郵件獲取顧客"""
    try:
        customer = custom_service.get_customer_by_email(db, customer_email)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer
    except Exception as e:
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{customer_uuid}", response_model=CustomerResponse)
def update_customer(
    customer_uuid: str,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_session),
):
    """更新顧客資訊"""
    try:
        customer = custom_service.update_customer(
            db=db,
            customer_uuid=customer_uuid,
            customer_name=customer_data.customer_name,
            customer_phone=customer_data.customer_phone,
        )
        db.commit()
        return customer
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        db.rollback()
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{customer_uuid}")
def delete_customer(customer_uuid: str, db: Session = Depends(get_session)):
    """刪除顧客"""
    try:
        custom_service.delete_customer(db, customer_uuid)
        db.commit()
        return {"message": "Customer deleted successfully"}
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        db.rollback()
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
