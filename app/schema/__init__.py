from .auth_schema import (
    Token,
    LoginToken,
    TokenData,
    LoginData,
    CustomLoginData,
    CustomDineVerify,
    CustomTakeOutVerify,
)
from .desk_schema import (
    DeskBindingRequest,
    DeskBindingResponse,
    ReleaseBindingRequest,
    ReleaseBindingResponse,
)
from .menu_schema import (
    MenuItemCreate,
    MenuItemUpdate,
    MenuItemResponse,
    MenuItemWithInventory,
)
from .order_schema import (
    OrderItemCreate,
    OrderItemResponse,
    OrderCreate,
    OrderResponse,
    OrderUpdate,
    OrderStatusUpdate
)
from .payment_schema import PaymentCreate, PaymentResponse
from .report_schema import DailySalesReport, PopularItemReport
from .user_schema import UserData, UserCreate, UserUpdate
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


# 菜單相關 Schema 補充
class MenuItemWithInventoryResponse(MenuItemResponse):
    stock_quantity: int = 0


# 報表相關 Schema 補充
class PaymentMethodBreakdown(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    method: str
    count: int
    amount: float


class HourlySales(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    hour: int
    count: int
    amount: float


class DailySalesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: str
    order_count: int
    total_sales: float
    avg_order_amount: float
    payment_methods: List[PaymentMethodBreakdown]
    hourly_sales: List[HourlySales]


class PopularItemDetail(BaseModel):
    uuid: str
    name: str
    category: str
    price: float
    total_quantity: int
    total_sales: float
    percentage_of_sales: Optional[float] = None


class PopularItemsResponse(BaseModel):
    period_days: int
    start_date: str
    end_date: str
    items: List[PopularItemDetail]


class InventoryItemDetail(BaseModel):
    uuid: str
    name: str
    category: str
    stock_quantity: int
    available: bool


class InventoryStatusResponse(BaseModel):
    out_of_stock_count: int
    low_inventory_count: int
    healthy_inventory_count: int
    out_of_stock: List[InventoryItemDetail]
    low_inventory: List[InventoryItemDetail]
    healthy_inventory: List[InventoryItemDetail]
    low_inventory_count: int
    healthy_inventory_count: int
    out_of_stock: List[InventoryItemDetail]
    low_inventory: List[InventoryItemDetail]
    healthy_inventory: List[InventoryItemDetail]


# 補充缺失的 schema 導入
from .login_schema import (
    LoginData,
    LoginToken,
    Token,
    CustomLoginData,
    CustomTakeOutVerify,
    CustomDineVerify,
    DeskBindingRequest,
    DeskBindingResponse,
    ReleaseBindingRequest,
    ReleaseBindingResponse,

)
