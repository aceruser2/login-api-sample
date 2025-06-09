from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class OrderItemCreate(BaseModel):
    item_uuid: str
    quantity: int
    note: Optional[str] = None


class OrderItemResponse(BaseModel):
    uuid: str
    item_uuid: str
    order_uuid: str
    quantity: int
    subtotal: int
    note: Optional[str]
    item_name: str
    item_price: int
    create_dt: datetime
    update_dt: datetime


class OrderCreate(BaseModel):
    customer_uuid: str
    desk_uuid: Optional[str] = None
    order_type: str
    note: Optional[str] = None
    items: List[OrderItemCreate]


class OrderResponse(BaseModel):
    uuid: str
    customer_uuid: str
    desk_uuid: Optional[str]
    total_amount: int
    status: int  # 0: pending, 1: cooking, 2: completed, 3: cancelled
    order_type: str
    note: Optional[str]
    items: List[OrderItemResponse]
    create_dt: datetime
    update_dt: datetime
