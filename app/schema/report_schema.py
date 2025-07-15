from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class DailySalesReport(BaseModel):
    """日銷售報表 Schema"""

    model_config = ConfigDict(from_attributes=True)

    date: datetime
    total_sales: float
    total_orders: int
    average_order_value: float


class PopularItemReport(BaseModel):
    """熱門商品報表 Schema"""

    model_config = ConfigDict(from_attributes=True)

    item_uuid: str
    item_name: str
    quantity_sold: int
    total_sales: float
