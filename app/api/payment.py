from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import app
from app.services.payment_service import create_payment
from app.schema import PaymentCreate, PaymentResponse
from app.extension.sql_ext import get_session
from app.extension.jwt_config import get_current_user
import logging

log = logging.getLogger(__name__)


@app.post("/payments/", response_model=PaymentResponse)
async def process_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    # 只有員工可以處理支付
    if hasattr(current_user, "user_status") and current_user.user_status in [
        2,
        3,
    ]:  # Customer
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can process payments",
        )
    try:
        result = create_payment(db=db, payment=payment)
        db.commit()
        return result
    except Exception as e:
        db.rollback()
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
