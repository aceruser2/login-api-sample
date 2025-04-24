from typing import List, Optional, Union, Dict
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.extension.emun_setting import OrderStatusEnum


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginToken(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    user_or_desk: Union[str, int] = None
    extra: Optional[int] = None


class UserData(BaseModel):
    uuid: UUID
    username: Optional[str] = None
    desk_number: Optional[int] = None
    info: Optional[Dict]
    email: str
    user_status: int
    creat_dt: datetime
    update_dt: datetime


class LoginData(BaseModel):
    password: str
    username: Optional[str] = None


class CustomLoginData(BaseModel):
    custom_name: str
    phone: str
    email: str
    use_in_restaurants: bool


class DeskBindingRequest(BaseModel):
    customer_phone: str
    desk_uuid: str


class DeskBindingResponse(BaseModel):
    desk_uuid: str
    customer_uuid: UUID
    create_dt: datetime


class ReleaseBindingRequest(BaseModel):
    customer_phone: str


class ReleaseBindingResponse(BaseModel):
    message: str


class MenuItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: int
    category: str
    image_url: Optional[str] = None


class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    available: Optional[bool] = None


class MenuItemResponse(BaseModel):
    uuid: str
    name: str
    description: Optional[str]
    price: int
    category: str
    image_url: Optional[str]
    available: bool
    create_dt: datetime
    update_dt: datetime


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
    items: list[OrderItemCreate]


class OrderResponse(BaseModel):
    uuid: str
    customer_uuid: str
    desk_uuid: Optional[str]
    total_amount: int
    status: int  # 0: pending, 1: cooking, 2: completed, 3: cancelled
    order_type: str
    note: Optional[str]
    items: list[OrderItemResponse]
    create_dt: datetime
    update_dt: datetime


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


class DailySalesReport(BaseModel):
    date: datetime
    total_sales: int
    total_orders: int
    average_order_value: float


class PopularItemReport(BaseModel):
    item_uuid: str
    item_name: str
    quantity_sold: int
    total_sales: int
