from typing import Optional
from pydantic import BaseModel, ConfigDict


class MenuItemCreate(BaseModel):
    """創建菜單項目的 Schema"""

    name: str
    description: Optional[str] = None
    price: int
    category: str
    image_url: Optional[str] = None
    available: bool = True


class MenuItemUpdate(BaseModel):
    """更新菜單項目的 Schema"""

    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    available: Optional[bool] = None


class MenuItemResponse(BaseModel):
    """菜單項目回應的 Schema"""

    model_config = ConfigDict(from_attributes=True)

    uuid: str
    name: str
    description: Optional[str]
    price: int
    category: str
    image_url: Optional[str]
    available: bool


class MenuItemWithInventory(BaseModel):
    """帶庫存信息的菜單項目（內部使用）"""

    model_config = ConfigDict(from_attributes=True)

    uuid: str
    name: str
    description: Optional[str]
    price: int
    category: str
    image_url: Optional[str]
    available: bool
    stock_quantity: int = 0
    available: bool
    stock_quantity: int = 0
    stock_quantity: int = 0
