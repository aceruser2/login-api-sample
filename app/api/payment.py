from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app import app
from app.adapter.payment import create_payment
from app.adapter.schema import PaymentCreate, PaymentResponse
from app.extension.sql_ext import get_session
from app.extension.jwt_config import get_current_user


@app.post("/payments/", response_model=PaymentResponse)
async def process_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    return create_payment(db=db, payment=payment)
