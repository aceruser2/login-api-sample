from typing import Optional
from pydantic import BaseModel, ConfigDict


class PaymentCreate(BaseModel):
    """創建支付的 Schema"""

    order_uuid: str
    payment_method: str
    amount_paid: int
    payment_note: Optional[str] = None


class PaymentResponse(BaseModel):
    """支付回應的 Schema"""

    model_config = ConfigDict(from_attributes=True)

    uuid: str
    order_uuid: str
    payment_method: str
    amount_paid: int
    payment_note: Optional[str]
    create_dt: str
