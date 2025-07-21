from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import app
from app.services.payment_service import create_payment
from app.schema import PaymentCreate, PaymentResponse
from app.extension.sql_ext import get_session
from app.extension.jwt_config import get_current_user
from app.utils.permission_checker import PermissionChecker
import logging
from typing import Tuple

log = logging.getLogger(__name__)


@app.post("/payments/", response_model=PaymentResponse)
async def process_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_session),
    user_data: Tuple = Depends(get_current_user),
):
    """處理支付（需要支付管理權限）"""
    PermissionChecker.require_staff_with_permission(
        user_data, db, "payment_management", "can_create"
    )
    try:
        result = create_payment(db=db, payment=payment)
        db.commit()
        return result
    except Exception as e:
        db.rollback()
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
