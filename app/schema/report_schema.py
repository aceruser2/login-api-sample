from datetime import datetime
from pydantic import BaseModel


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
