# POS 系統後端 API 規格書

---

## 一、系統架構

- 採用 FastAPI 三層架構（API / Service / Model / Schema）。
- 所有資料存取皆透過 SQLAlchemy 2.0 新式查詢語法。
- 所有資料進出皆經由 Pydantic Schema。
- API 層負責交易管理（commit/rollback）、錯誤捕捉與 HTTPException 轉換。
- Service 層僅處理商業邏輯，不 commit/rollback、不處理 HTTP Response/Request。

---

## 二、主要功能模組

### 1. 顧客管理

- 註冊/查詢顧客（以 email 為唯一鍵，若已存在則直接回傳現有顧客）。
- 顧客資料欄位：uuid, customer_name, customer_phone, email, is_verified, soft_delete, create_dt, update_dt。
- 支援信箱驗證流程確保真實顧客。

### 2. 桌位管理

- 建立、查詢、更新、刪除桌位。
- 桌位綁定（DeskCustomer）：顧客與桌位一對一綁定，綁定有效期 1 小時，結帳或手動解除時 soft_delete。
- 單一顧客一次僅能綁定一個桌位，同時保持自動過期機制。

### 3. 登入與驗證

- 支援員工與顧客登入（JWT Token）。
- 顧客登入支援信箱驗證碼流程（替代簡訊驗證）。
- 防止濫發驗證碼，驗證碼有效期 15 分鐘，冷卻時間 5 分鐘。
- JWT Token 包含訪問令牌與刷新令牌機制。

### 4. 訂單管理

- 建立訂單（Order, OrderItem）與庫存檢查機制。
- 查詢訂單（顧客僅能查詢自己訂單，員工可查詢全部）。
- 修改訂單狀態（pending, cooking, completed, cancelled）。
- 取消訂單功能並回復庫存。

### 5. 支付/結帳

- 建立支付紀錄（Payment）並支援多種支付方式。
- 結帳時自動將訂單狀態設為 completed，並自動解除桌位綁定（DeskCustomer.soft_delete = True）。
- 支持訂單金額檢查與防止重複結帳。

### 6. 庫存管理

- 菜單項目庫存追蹤與自動更新。
- 庫存不足時防止下單，確保良好用戶體驗。
- 低庫存警告與庫存狀態報表。

### 7. 報表

- 日營業額報表（DailySalesReport）：日期、總銷售額、訂單數、平均訂單金額。
- 熱門品項報表（PopularItemReport）：品項、銷量、銷售額、佔比分析。
- 庫存狀態報表（InventoryStatusReport）：缺貨、低庫存、正常庫存分類。
- 支援按時段、支付方式等多維度分析。

---

## 三、API 路徑與行為

| 功能                 | 方法 | 路徑                           | 權限/說明                              |
|----------------------|------|--------------------------------|---------------------------------------|
| 員工登入             | POST | `/token/staff`                 | 驗證員工帳號密碼並返回令牌             |
| 刷新員工令牌         | POST | `/refresh/staff`               | 使用刷新令牌獲取新的訪問令牌           |
| 顧客發送驗證碼       | POST | `/custom/email-send-code`      | 發送電子郵件驗證碼，冷卻時間5分鐘      |
| 顧客內用驗證         | POST | `/verify/dine-in`              | 驗證碼確認並綁定桌位                   |
| 顧客外帶驗證         | POST | `/verify/takeout`              | 驗證碼確認（不綁定桌位）               |
| 顧客綁定桌位         | POST | `/desk-customer/`              | 綁定桌號，1 小時內有效                 |
| 查詢桌位綁定         | GET  | `/desk-customer/active`        | 查詢 1 小時內有效綁定                  |
| 解除桌位綁定         | POST | `/desk-customer/release`       | 結帳或手動解除                         |
| 建立訂單             | POST | `/orders/`                     | 顧客只能為自己建立                     |
| 查詢訂單             | GET  | `/orders/`                     | 員工查全部，顧客查自己                 |
| 修改訂單狀態         | PUT  | `/orders/{order_uuid}/status`  | 只有員工可操作                         |
| 支付/結帳            | POST | `/payments/`                   | 結帳時自動解除桌位綁定                 |
| 菜單項目列表         | GET  | `/menu/items/`                 | 獲取菜單項目，可按類別過濾             |
| 帶庫存菜單項目       | GET  | `/menu/items-with-inventory/`  | 獲取含庫存資訊的菜單項目               |
| 日營業額報表         | GET  | `/reports/daily-sales`         | 員工專用，可指定日期                   |
| 熱門品項報表         | GET  | `/reports/popular-items`       | 員工專用，可指定時間範圍               |
| 庫存狀態報表         | GET  | `/reports/inventory`           | 員工專用，顯示庫存狀態分類             |

---

## 四、資料表設計（重點欄位）

### Customer
- uuid, customer_name, customer_phone, email, is_verified, soft_delete, create_dt, update_dt

### Desk
- uuid, desk_name, soft_delete, create_dt, update_dt

### DeskCustomer
- id, desk_uuid, customer_uuid, soft_delete, create_dt, update_dt

### Order
- uuid, customer_uuid, desk_uuid, total_amount, status, order_type, note, soft_delete, create_dt, update_dt

### OrderItem
- uuid, order_uuid, item_uuid, quantity, unit_price, subtotal, note, status, soft_delete, create_dt, update_dt

### Payment
- uuid, order_uuid, payment_method, amount_paid, payment_note, soft_delete, create_dt, update_dt

### MenuItem
- uuid, name, description, price, category, image_url, available, stock_quantity, soft_delete, create_dt, update_dt

### Inventory
- uuid, menu_item_uuid, stock_quantity, low_stock_threshold, soft_delete, create_dt, update_dt

---

## 五、商業邏輯摘要

- 顧客同時只能綁定一個桌位，且綁定有效期 1 小時。
- 結帳時自動解除桌位綁定。
- 訂單狀態流轉：pending → cooking → completed → cancelled。
- 庫存檢查在下單時進行，支持低庫存警告。
- 支付時檢查訂單金額並自動更新庫存。
- 所有查詢皆需過濾 soft_delete。
- 所有 API 需驗證 JWT Token（除了登入相關端點）。
- Service 層僅丟出 Python Exception，API 層負責 commit/rollback 與 HTTPException 轉換。
- 查詢單一模型請用 SQLAlchemy 2.0 style：`select(...)` + `.scalar_one_or_none()`。

---

## 六、錯誤處理與日誌

- API 層 except 區塊皆需 log.critical(e, exc_info=True)。
- 所有異常皆轉為 HTTPException 回傳。
- 驗證失敗時提供明確的錯誤訊息。
- 支援多層異常處理確保系統穩定性。

---

## 七、系統部署與操作方法

### 環境準備

1. **安裝依賴**
   ```bash
   pip install -r requirements.txt
   ```

2. **環境變數設定**
   - 複製 `.env.example` 到 `.env` 並設定：
   ```
   # 資料庫連線
   drivername=postgresql+psycopg2
   db_user=your_db_user
   db_pass=your_db_password
   db_host=localhost
   db_port=5432
   dbname=pos_system
   
   # JWT 設定
   SECRET_KEY=your_secret_key
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   
   # Email 設定
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   MAIL_FROM=your-email@gmail.com
   MAIL_PORT=587
   MAIL_SERVER=smtp.gmail.com
   ```

3. **資料庫遷移**
   ```bash
   alembic upgrade head
   ```

### 啟動服務

```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

### 測試

1. **執行單元測試**
   ```bash
   pytest tests/
   ```

2. **API 文檔訪問**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### 常見操作流程

1. **員工登入**
   - 使用系統預設管理員帳號 (admin/admin123) 登入
   - 獲取並保存 JWT token 用於後續操作

2. **桌位管理**
   - 建立桌位 (`POST /desk/create`)
   - 查看所有桌位 (`GET /desks/`)

3. **顧客註冊與登入**
   - 發送電子郵件驗證碼 (`POST /custom/email-send-code`)
   - 驗證內用顧客並綁定桌位 (`POST /verify/dine-in`)
   - 驗證外帶顧客 (`POST /verify/takeout`)

4. **點餐流程**
   - 查看菜單 (`GET /menu/items-with-inventory/`)
   - 建立訂單 (`POST /orders/`)
   - 訂單狀態更新 (`PUT /orders/{order_uuid}/status`)
   - 完成支付 (`POST /payments/`)

5. **報表查詢**
   - 日營業額報表 (`GET /reports/daily-sales`)
   - 熱門品項報表 (`GET /reports/popular-items`)
   - 庫存狀態報表 (`GET /reports/inventory`)

---

## 八、擴充建議

- 可擴充會員積分、促銷活動功能。
- 整合第三方支付系統。
- 預約系統與排隊管理。
- 報表可細分時段、品類等多維度分析。
- 實現庫存預警與自動補貨提醒。
- 建立員工績效統計功能。

---

本規格書可作為後端開發、測試與前後端協作的依據。
