# POS 系統操作指南

此文檔提供系統常見操作流程與 API 使用範例，幫助開發者與維護人員理解系統運作方式。

## 目錄

1. [系統初始化](#系統初始化)
2. [員工管理](#員工管理)
3. [顧客登入流程](#顧客登入流程)
4. [桌位管理](#桌位管理)
5. [訂單管理](#訂單管理)
6. [支付流程](#支付流程)
7. [報表查詢](#報表查詢)
8. [常見問題排除](#常見問題排除)
9. [自動化測試](#自動化測試)

---

## 系統初始化

### 啟動服務

```bash
# 開發模式啟動
uvicorn server:app --host 0.0.0.0 --port 8000 --reload

# 生產環境啟動
uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
```

### 初始化資料庫

```bash
# 執行資料庫遷移
alembic upgrade head

# 若需要建立新的遷移檔案
alembic revision --autogenerate -m "your migration message"
```

### 系統預設帳號

系統初始化時會自動建立管理員帳號：
- 使用者名稱：admin
- 密碼：admin123（可在環境變數中修改）

---

## 員工管理

### 員工登入

```
POST /token/staff

Request:
{
  "username": "admin",
  "password": "admin123"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzM4NCIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 刷新令牌

```
POST /refresh/staff

Headers:
Authorization: Bearer <refresh_token>

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## 顧客登入流程

### 步驟 1: 發送電子郵件驗證碼

```
POST /custom/email-send-code

Request:
{
  "custom_name": "測試顧客",
  "phone": "0912345678",
  "email": "customer@example.com"
}

Response:
{
  "message": "Verification code sent",
  "require_verification": true,
  "is_new_user": true  // 如果是新用戶則為 true
}
```

### 步驟 2A: 內用顧客驗證（綁定桌位）

```
POST /verify/dine-in

Request:
{
  "email": "customer@example.com",
  "verify_code": "123456",  // 從郵件中獲取的驗證碼
  "desk_uuid": "desk-uuid-1"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzM4NCIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 步驟 2B: 外帶顧客驗證

```
POST /verify/takeout

Request:
{
  "email": "customer@example.com",
  "verify_code": "123456",  // 從郵件中獲取的驗證碼
  "phone": "0912345678"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzM4NCIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## 桌位管理

### 建立新桌位

```
POST /desk/create?desk_name=Table%201

Headers:
Authorization: Bearer <staff_access_token>

Response:
{
  "uuid": "desk-uuid-1",
  "desk_name": "Table 1",
  "soft_delete": false,
  "create_dt": "2023-01-01T12:00:00",
  "update_dt": "2023-01-01T12:00:00"
}
```

### 查詢所有桌位

```
GET /desks/?skip=0&limit=10

Headers:
Authorization: Bearer <staff_access_token>

Response:
{
  "total": 5,
  "skip": 0,
  "limit": 10,
  "desks": [
    {
      "uuid": "desk-uuid-1",
      "desk_name": "Table 1",
      "soft_delete": false,
      "create_dt": "2023-01-01T12:00:00",
      "update_dt": "2023-01-01T12:00:00"
    },
    // ... 其他桌位
  ]
}
```

### 查詢桌位綁定

```
GET /desk-customer/active?customer_email=customer@example.com

Headers:
Authorization: Bearer <access_token>

Response:
{
  "desk_uuid": "desk-uuid-1",
  "customer_uuid": "customer-uuid-1",
  "create_dt": "2023-01-01T12:00:00"
}
```

### 解除桌位綁定

```
POST /desk-customer/release

Headers:
Authorization: Bearer <access_token>

Request:
{
  "customer_email": "customer@example.com"
}

Response:
{
  "message": "desk unbound"
}
```

---

## 訂單管理

### 取得菜單項目（含庫存）

```
GET /menu/items-with-inventory/?category=主餐

Headers:
Authorization: Bearer <access_token>

Response:
[
  {
    "uuid": "item-uuid-1",
    "name": "牛肉漢堡",
    "description": "100%純牛肉",
    "price": 120,
    "category": "主餐",
    "image_url": "https://example.com/burger.jpg",
    "available": true,
    "stock_quantity": 50,
    "create_dt": "2023-01-01T10:00:00",
    "update_dt": "2023-01-01T10:00:00"
  },
  // ... 其他菜單項目
]
```

### 建立訂單

```
POST /orders/

Headers:
Authorization: Bearer <access_token>

Request:
{
  "customer_uuid": "customer-uuid-1",
  "desk_uuid": "desk-uuid-1",  // 外帶可為 null
  "order_type": "dine_in",     // 或 "takeout"
  "note": "不要加洋蔥",
  "items": [
    {
      "item_uuid": "item-uuid-1",
      "quantity": 2,
      "note": "加辣"
    },
    {
      "item_uuid": "item-uuid-2",
      "quantity": 1,
      "note": null
    }
  ]
}

Response:
{
  "uuid": "order-uuid-1",
  "customer_uuid": "customer-uuid-1",
  "desk_uuid": "desk-uuid-1",
  "total_amount": 340,
  "status": 0,  // pending
  "order_type": "dine_in",
  "note": "不要加洋蔥",
  "items": [
    // 訂單項目詳情
  ],
  "create_dt": "2023-01-01T13:00:00",
  "update_dt": "2023-01-01T13:00:00"
}
```

### 查詢訂單

```
GET /orders/?skip=0&limit=10&status=pending

Headers:
Authorization: Bearer <access_token>

Response:
[
  {
    "uuid": "order-uuid-1",
    "customer_uuid": "customer-uuid-1",
    "desk_uuid": "desk-uuid-1",
    "total_amount": 340,
    "status": 0,
    "order_type": "dine_in",
    "note": "不要加洋蔥",
    "items": [
      // 訂單項目詳情
    ],
    "create_dt": "2023-01-01T13:00:00",
    "update_dt": "2023-01-01T13:00:00"
  }
  // ... 其他訂單
]
```

### 更新訂單狀態

```
PUT /orders/{order_uuid}/status?status=cooking

Headers:
Authorization: Bearer <staff_access_token>

Response:
{
  "uuid": "order-uuid-1",
  "status": "cooking",
  "update_dt": "2023-01-01T13:15:00"
}
```

---

## 支付流程

### 處理支付

```
POST /payments/

Headers:
Authorization: Bearer <access_token>

Request:
{
  "order_uuid": "order-uuid-1",
  "payment_method": "cash",  // 或 "credit_card", "mobile_payment"
  "amount_paid": 340,
  "payment_note": "找零20元"
}

Response:
{
  "uuid": "payment-uuid-1",
  "order_uuid": "order-uuid-1",
  "payment_method": "cash",
  "amount_paid": 340,
  "payment_note": "找零20元",
  "create_dt": "2023-01-01T14:00:00"
}
```

---

## 報表查詢

### 日銷售報表

```
GET /reports/daily-sales?date=2023-01-01

Headers:
Authorization: Bearer <staff_access_token>

Response:
{
  "date": "2023-01-01",
  "order_count": 25,
  "total_sales": 12500,
  "avg_order_amount": 500,
  "payment_methods": [
    {
      "method": "cash",
      "count": 15,
      "amount": 7500
    },
    {
      "method": "credit_card",
      "count": 10,
      "amount": 5000
    }
  ],
  "hourly_sales": [
    {
      "hour": 10,
      "count": 5,
      "amount": 2500
    },
    // ... 其他時段
  ]
}
```

### 熱門品項報表

```
GET /reports/popular-items?days=7&limit=10

Headers:
Authorization: Bearer <staff_access_token>

Response:
{
  "period_days": 7,
  "start_date": "2023-01-01",
  "end_date": "2023-01-07",
  "items": [
    {
      "uuid": "item-uuid-1",
      "name": "牛肉漢堡",
      "category": "主餐",
      "price": 120,
      "total_quantity": 150,
      "total_sales": 18000,
      "percentage_of_sales": 35.5
    },
    // ... 其他熱門品項
  ]
}
```

### 庫存狀態報表

```
GET /reports/inventory

Headers:
Authorization: Bearer <staff_access_token>

Response:
{
  "out_of_stock_count": 3,
  "low_inventory_count": 5,
  "healthy_inventory_count": 20,
  "out_of_stock": [
    {
      "uuid": "item-uuid-4",
      "name": "起司蛋糕",
      "category": "甜點",
      "stock_quantity": 0,
      "available": false
    },
    // ... 其他缺貨品項
  ],
  "low_inventory": [
    // 低庫存品項
  ],
  "healthy_inventory": [
    // 庫存正常品項
  ]
}
```

---

## 常見問題排除

### 驗證碼相關問題

1. **無法收到驗證碼**
   - 檢查郵件垃圾箱
   - 確認信箱設置正確
   - 檢查環境變數 MAIL_* 設置是否正確

2. **驗證碼失效**
   - 驗證碼有效期為 15 分鐘，過期需重新獲取
   - 冷卻時間 5 分鐘內不可重複發送

### 權限問題

- 確保使用正確的令牌（員工/顧客）
- 檢查令牌是否過期
- 員工特定功能需要員工權限令牌

### 庫存問題

- 商品顯示缺貨：可在管理後台補充庫存
- 下單時庫存不足：系統會自動阻止並提示庫存不足

### 資料庫連接問題

- 檢查環境變數中資料庫連接設置
- 確保資料庫服務正常運行
- 資料庫連接池問題可調整 pool_size 和 max_overflow

### 系統效能優化

- 使用 Redis 緩存熱門菜單項目
- 定期清理過期的桌位綁定記錄
- 報表查詢建議在非高峰期執行

---

## 自動化測試

### 單元測試 (Pytest)

```bash
# 運行所有測試
pytest

# 運行指定測試檔案
pytest tests/test_api.py

# 運行特定測試函數
pytest tests/test_api.py::test_staff_login

# 顯示詳細輸出
pytest -v
```

### 端到端測試 (Selenium)

```bash
# 需要先啟動前端和後端服務
# 前端: npm start (在前端目錄下)
# 後端: uvicorn server:app --host 0.0.0.0 --port 8000

# 設定環境變數
export FRONTEND_URL=http://localhost:3000
export TEST_ADMIN_USERNAME=admin
export TEST_ADMIN_PASSWORD=admin123
export SCREENSHOT_DIR=./screenshots

# 運行 Selenium 測試
pytest tests/test_selenium.py

# 查看截圖
# 截圖會保存在 SCREENSHOT_DIR 指定的目錄中
```

測試過程中的螢幕截圖會按時間戳命名並保存在截圖目錄中，可用於分析測試失敗的原因或驗證測試步驟的正確性。

### CI/CD 整合

本專案的測試已整合進 CI/CD 流程。每次提交代碼後，系統會自動執行:

1. 單元測試 (pytest)
2. 端到端測試 (selenium, 在 headless 模式下)
3. 代碼覆蓋率分析

CI 流程如果發現測試失敗，會阻止代碼合併至主分支。

---

如有其他問題，請聯繫系統管理員或參考專案 GitHub 倉庫的 Issues 區。
