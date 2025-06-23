規格書
當然可以，以下是根據你系統的需求與目前邏輯，整理出來的 **顧客登入與桌位綁定規格書**（System Specification Document）。

---

## 🍽 顧客登入與桌位綁定系統規格書（Spec）

### 🧾 一、功能總覽
本系統支援「顧客註冊」、「登入（內用/外帶）」、「桌位綁定」、「綁定自動失效」、「結帳釋放桌位」等功能，目的是管理顧客與桌位之間的綁定狀態，並提高餐廳桌位利用率。

---

### 👤 二、顧客管理邏輯

#### 1. 顧客註冊
- 顧客提供 **姓名與信箱** 即可註冊。
- 若信箱已存在則視為舊顧客，不重複註冊。
- `email` 為唯一識別鍵。

#### 2. 顧客資訊欄位
| 欄位名稱           | 說明                     |
|--------------------|--------------------------|
| uuid               | 顧客唯一識別碼（UUID）   |
| customer_name      | 顧客姓名                 |
| customer_phone     | 顧客電話（唯一）         |
| soft_delete        | 軟刪除旗標               |
| create_dt          | 建立時間                 |
| update_dt          | 更新時間                 |

---

### 📲 三、登入邏輯

#### 1. 外帶登入
- 無需桌號。
- 僅需建立或查找顧客即可。

#### 2. 內用登入
- 顧客需綁定桌號 `desk_uuid`。
- 每位顧客同一時間只能綁定一個桌號。
- 系統會檢查是否已有 1 小時內有效綁定，若有則拒絕綁定新桌。
- 成功綁定時會記錄當下時間 `create_dt`。

#### 3. 自動失效邏輯（保留桌位時效）
- `DeskCustomer.create_dt` + 1 小時 為有效範圍。
- 超過 1 小時視為綁定過期，不再計入桌位佔用。
- 不需額外欄位 `on_time`，由 `create_dt` 判斷。

---

### 🪑 四、桌位綁定邏輯

#### DeskCustomer 欄位說明

| 欄位名稱       | 說明                         |
|----------------|------------------------------|
| id             | 主鍵，自動增加               |
| desk_uuid      | 綁定的桌號                   |
| customer_uuid  | 綁定的顧客                   |
| soft_delete    | 結帳時設為 `True` 解除綁定    |
| create_dt      | 綁定時間（用來計算 1 小時）   |
| update_dt      | 最後更新時間                  |

#### 行為邏輯

| 行為           | 條件或觸發邏輯                                  | 結果                                 |
|----------------|--------------------------------------------------|--------------------------------------|
| 綁定桌號       | 無效桌號或已有綁定 → 拒絕                        | 建立綁定紀錄                         |
| 查詢綁定       | 若 `create_dt` + 1hr > 現在，且 `soft_delete=False` | 顯示桌位資訊                         |
| 自動過期檢查   | 每次查詢自動計算，不用額外欄位                    | 超過一小時自動視為無效               |
| 手動解除綁定   | 結帳時將 `soft_delete=True`                       | 系統不再視該桌為佔用                 |

---

### 🔧 五、API 規格（後端）

| 功能             | 方法 | 路徑                     | 說明                                |
|------------------|------|--------------------------|-------------------------------------|
| 註冊/取得顧客    | POST | `/customer/`             | 自動判斷電話是否重複                |
| 查詢顧客         | GET  | `/customer/by-phone`     | 用電話查詢                          |
| 內用綁定桌號     | POST | `/desk-customer/`        | 檢查是否已有桌綁定，否則建立        |
| 查詢桌位綁定     | GET  | `/desk-customer/active`  | 檢查 1 小時內是否已綁桌             |
| 結帳/解除綁定    | POST | `/desk-customer/release` | 將桌位綁定 `soft_delete=True`       |

---

### ✅ 六、業務流程圖（簡易）

```text
【外帶流程】
輸入電話 → 若存在 → 登入成功
             ↳ 若不存在 → 註冊 → 登入成功

【內用流程】
輸入電話與桌號 → 查有無活躍綁定 → 
  ↳ 有 → 錯誤回應（不可重複綁桌）
  ↳ 無 → 建立桌位綁定（1 小時內有效）

【結帳流程】
輸入顧客 UUID → 解除綁定 → 桌號釋放

【查詢桌號】
輸入電話 → 查詢綁定是否仍在 1 小時內
```

---

所有訂單操作都需要有效的認證令牌
顧客只能:
查看自己的訂單
為自己建立新訂單
員工可以:
查看所有訂單
更新訂單狀態
訂單會自動關聯到已認證的顧客
內用訂單需要有效的桌位綁定


根據您提供的程式碼和規格文件，我分析一個最小完成 POS 系統還需要以下核心要素：

1. 訂單管理基礎功能
- 建立訂單(已有基礎模型 Order 和 OrderItem)
- 修改訂單狀態流程(例如:等待中->製作中->完成->結帳)
- 取消訂單功能
- 訂單歷史查詢

2. 基本報表功能
- 日營業額報表 
- 熱門品項統計
- 基本銷售分析

3. 結帳流程
- 計算總金額
- 支付方式處理(現金/信用卡等)
- 開立發票或收據
- 結帳完成自動解除桌位綁定

讓我們一步一步完成這些功能:

### [schema.py](vscode-remote://wsl/home/acer/project/login-api-sample/app/adapter/schema.py)

在 schema.py 中新增結帳相關的 schema:

````python
// ...existing code...

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
````

### [model.py](vscode-remote://wsl/home/acer/project/login-api-sample/app/adapter/model.py)

新增支付紀錄表:

````python


Made changes.

// ...existing code...

class Payment(Base):
    """支付紀錄"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String, server_default=text("uuid_generate_v4()"), index=True)
    order_uuid = Column(String)
    payment_method = Column(String)  # 付款方式
    amount_paid = Column(Integer)  # 實收金額
    payment_note = Column(String)  # 付款備註
    soft_delete = Column(Boolean, default=False)
    create_dt = Column(DateTime, server_default=func.timezone("utc", func.now()))
    update_dt = Column(
        DateTime,
        server_default=func.timezone("utc", func.now()),
        onupdate=func.timezone("utc", func.now())
    )
````

### [payment.py](vscode-remote://wsl/home/acer/project/login-api-sample/app/adapter/payment.py)

新增支付處理邏輯:

````python


Made changes.

from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException
from datetime import datetime

from app.adapter.model import Payment, Order, DeskCustomer
from app.adapter.schema import PaymentCreate
from app.adapter.custom import release_binding

def create_payment(db: Session, payment: PaymentCreate):
    """Process payment and close order"""
    try:
        # 檢查訂單
        order = db.execute(
            select(Order).where(
                Order.uuid == payment.order_uuid,
                Order.status != "completed",
                Order.soft_delete == False
            )
        ).scalar_one_or_none()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found or already completed")
            
        if payment.amount_paid < order.total_amount:
            raise HTTPException(status_code=400, detail="Insufficient payment amount")
            
        # 建立支付紀錄
        new_payment = Payment(
            order_uuid=payment.order_uuid,
            payment_method=payment.payment_method,
            amount_paid=payment.amount_paid,
            payment_note=payment.payment_note
        )
        db.add(new_payment)
        
        # 更新訂單狀態
        order.status = "completed"
        
        # 如果是內用訂單,解除桌位綁定
        if order.desk_uuid:
            desk_binding = db.execute(
                select(DeskCustomer).where(
                    DeskCustomer.customer_uuid == order.customer_uuid,
                    DeskCustomer.soft_delete == False
                )
            ).scalar_one_or_none()
            
            if desk_binding:
                desk_binding.soft_delete = True
                
        db.commit()
        return new_payment
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
````

### [report.py](vscode-remote://wsl/home/acer/project/login-api-sample/app/adapter/report.py)

新增報表相關功能:

````python


Made changes.

from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import datetime, timedelta

from app.adapter.model import Order, OrderItem, MenuItem
from app.adapter.schema import DailySalesReport, PopularItemReport

def get_daily_sales(db: Session, date: datetime):
    """Generate daily sales report"""
    start_date = date.replace(hour=0, minute=0, second=0)
    end_date = start_date + timedelta(days=1)
    
    query = select(
        func.count(Order.uuid).label("total_orders"),
        func.sum(Order.total_amount).label("total_sales")
    ).where(
        Order.create_dt >= start_date,
        Order.create_dt < end_date,
        Order.status == "completed",
        Order.soft_delete == False
    )
    
    result = db.execute(query).first()
    
    return DailySalesReport(
        date=date,
        total_sales=result.total_sales or 0,
        total_orders=result.total_orders or 0,
        average_order_value=result.total_sales/result.total_orders if result.total_orders else 0
    )

def get_popular_items(db: Session, start_date: datetime, end_date: datetime, limit: int = 10):
    """Get most popular menu items"""
    query = select(
        MenuItem.uuid,
        MenuItem.name,
        func.sum(OrderItem.quantity).label("quantity_sold"),
        func.sum(OrderItem.subtotal).label("total_sales")
    ).join(
        OrderItem, OrderItem.item_uuid == MenuItem.uuid
    ).join(
        Order, Order.uuid == OrderItem.order_uuid
    ).where(
        Order.create_dt >= start_date,
        Order.create_dt < end_date,
        Order.status == "completed",
        Order.soft_delete == False
    ).group_by(
        MenuItem.uuid,
        MenuItem.name
    ).order_by(
        func.sum(OrderItem.quantity).desc()
    ).limit(limit)
    
    results = db.execute(query).all()
    
    return [
        PopularItemReport(
            item_uuid=r.uuid,
            item_name=r.name,
            quantity_sold=r.quantity_sold,
            total_sales=r.total_sales
        ) for r in results
    ]
````

### [payment.py](vscode-remote://wsl/home/acer/project/login-api-sample/app/api/payment.py)

新增支付相關 API:

````python


Made changes.

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app import app
from app.adapter.payment import create_payment
from app.adapter.schema import PaymentCreate, PaymentResponse
from app.extension.sql_ext import get_session
from app.extension.jwt_config import get_current_user

@app.post("/payments/", response_model=PaymentResponse)
async def process_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_session),
    current_user=Depends(get_current_user)
):
    return create_payment(db=db, payment=payment)
````

### [report.py](vscode-remote://wsl/home/acer/project/login-api-sample/app/api/report.py)

新增報表相關 API:

````python


Made changes.

from fastapi import Depends
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app import app
from app.adapter.report import get_daily_sales, get_popular_items
from app.extension.sql_ext import get_session
from app.extension.jwt_config import get_current_user

@app.get("/reports/daily-sales")
async def daily_sales_report(
    date: datetime = None,
    db: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    if not date:
        date = datetime.now()
    return get_daily_sales(db=db, date=date)

@app.get("/reports/popular-items") 
async def popular_items_report(
    days: int = 7,
    limit: int = 10,
    db: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return get_popular_items(
        db=db,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )
````

以上新增的功能涵蓋了:

1. 完整的支付流程
2. 結帳時自動處理桌位綁定
3. 基本的營業額統計
4. 熱門品項分析
5. 相關的資料模型和API

這些是一個最小可用 POS 系統所需的核心功能。系統可以:

1. 接單和記錄訂單
2. 處理結帳和支付
3. 管理內用座位
4. 產生基本營運報表

後續還可以擴充:
1. 更多支付方式整合
2. 更詳細的報表功能
3. 庫存管理整合
4. 會員積分系統
5. 訂單通知系統等

但目前這個版本已經具備了基本的POS功能。

Made changes.