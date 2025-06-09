from fastapi import Depends, HTTPException
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
    try:
        payment_obj = create_payment(db=db, payment=payment)
        db.commit()
        return payment_obj
    except Exception as e:
        db.rollback()
        log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
