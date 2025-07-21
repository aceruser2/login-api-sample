from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.extension.emun_setting import OrderStatusEnum


class OrderItemCreate(BaseModel):
    """創建訂單項目的 Schema"""

    item_uuid: str
    quantity: int
    note: Optional[str] = None


class OrderItemResponse(BaseModel):
    """訂單項目回應的 Schema"""

    model_config = ConfigDict(from_attributes=True)

    uuid: str
    item_uuid: str
    quantity: int
    unit_price: int
    subtotal: int
    note: Optional[str]
    status: int


class OrderCreate(BaseModel):
    """創建訂單的 Schema"""

    customer_uuid: str
    desk_uuid: Optional[str] = None
    order_type: str
    items: List[OrderItemCreate]
    note: Optional[str] = None


class OrderResponse(BaseModel):
    """訂單回應的 Schema"""

    model_config = ConfigDict(from_attributes=True)

    uuid: str
    customer_uuid: str
    desk_uuid: Optional[str]
    total_amount: int
    status: int
    order_type: str
    note: Optional[str]
    create_dt: datetime
    update_dt: datetime


class OrderUpdate(BaseModel):
    """更新訂單的 Schema"""

    items: Optional[List[OrderItemCreate]] = None
    note: Optional[str] = None


class OrderStatusUpdate(BaseModel):
    """更新訂單狀態的 Schema"""

    status: OrderStatusEnum  # 使用 Enum 進行驗證
