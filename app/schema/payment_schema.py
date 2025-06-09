from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class PaymentCreate(BaseModel):
    order_uuid: str
    payment_method: str  # cash, credit_card, line_pay etc
    amount_paid: int
    payment_note: Optional[str] = None


class PaymentResponse(BaseModel):
    uuid: str
    order_uuid: str
    payment_method: str
    amount_paid: int
    payment_note: Optional[str]
    create_dt: datetime
