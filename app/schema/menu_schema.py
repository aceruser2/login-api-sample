from typing import Optional
from datetime import datetime
from pydantic import BaseModel


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
