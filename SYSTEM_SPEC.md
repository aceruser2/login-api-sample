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
- 顧客資料欄位：uuid, customer_name, customer_phone, email, soft_delete, create_dt, update_dt。

### 2. 桌位管理

- 建立、查詢、更新、刪除桌位。
- 桌位綁定（DeskCustomer）：顧客與桌位一對一綁定，綁定有效期 1 小時，結帳或手動解除時 soft_delete。

### 3. 登入與驗證

- 支援員工與顧客登入（JWT Token）。
- 顧客登入支援信箱驗證碼流程。
- 防止濫發驗證碼，驗證碼有效期與冷卻時間可設定。

### 4. 訂單管理

- 建立訂單（Order, OrderItem）。
- 查詢訂單（顧客僅能查詢自己訂單，員工可查詢全部）。
- 修改訂單狀態（pending, cooking, completed, cancelled）。
- 取消訂單。

### 5. 支付/結帳

- 建立支付紀錄（Payment）。
- 結帳時自動將訂單狀態設為 completed，並自動解除桌位綁定（DeskCustomer.soft_delete = True）。

### 6. 報表

- 日營業額報表（DailySalesReport）：日期、總銷售額、訂單數、平均訂單金額。
- 熱門品項報表（PopularItemReport）：品項、銷量、銷售額。

---

## 三、API 路徑與行為

| 功能             | 方法 | 路徑                        | 權限/說明                       |
|------------------|------|-----------------------------|----------------------------------|
| 顧客註冊/查詢    | POST | `/customer/`                | 傳入電話，若存在直接回傳         |
| 查詢顧客         | GET  | `/customer/by-phone`        | 以電話查詢                       |
| 內用綁定桌號     | POST | `/desk-customer/`           | 綁定桌號，1 小時內有效           |
| 查詢桌位綁定     | GET  | `/desk-customer/active`     | 查詢 1 小時內有效綁定            |
| 解除桌位綁定     | POST | `/desk-customer/release`    | 結帳或手動解除                   |
| 建立訂單         | POST | `/orders/`                  | 顧客只能為自己建立               |
| 查詢訂單         | GET  | `/orders/`                  | 員工查全部，顧客查自己           |
| 修改訂單狀態     | PUT  | `/orders/{order_uuid}/status` | 只有員工可操作                   |
| 支付/結帳        | POST | `/payments/`                | 結帳時自動解除桌位綁定           |
| 日營業額報表     | GET  | `/reports/daily-sales`      | 員工專用                          |
| 熱門品項報表     | GET  | `/reports/popular-items`    | 員工專用                          |

---

## 四、資料表設計（重點欄位）

### Customer
- uuid, customer_name, customer_phone, soft_delete, create_dt, update_dt

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
- uuid, name, description, price, category, image_url, available, soft_delete, create_dt, update_dt

---

## 五、商業邏輯摘要

- 顧客同時只能綁定一個桌位，且綁定有效期 1 小時。
- 結帳時自動解除桌位綁定。
- 訂單狀態流轉：pending → cooking → completed → cancelled。
- 所有查詢皆需過濾 soft_delete。
- 所有 API 需驗證 JWT Token。
- Service 層僅丟出 Python Exception，API 層負責 commit/rollback 與 HTTPException 轉換。
- 查詢單一模型請用 SQLAlchemy 2.0 style：`select(...)` + `.scalar_one_or_none()`。

---

## 六、錯誤處理與日誌

- API 層 except 區塊皆需 log.critical(e, exc_info=True)。
- 所有異常皆轉為 HTTPException 回傳。

---

## 七、擴充建議

- 可擴充會員積分、庫存管理、通知推播等功能。
- 報表可細分時段、品類等多維度分析。

---

本規格書可作為後端開發、測試與前後端協作的依據。
