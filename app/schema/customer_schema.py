from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class CustomerBase(BaseModel):
    customer_name: str
    customer_phone: str
    email: EmailStr


class CustomerCreate(CustomerBase):
    is_verified: bool = False


class CustomerUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None


class CustomerResponse(CustomerBase):
    uuid: str
    is_verified: bool
    create_dt: datetime
    update_dt: datetime

    
