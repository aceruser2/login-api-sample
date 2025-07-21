# 餐廳 POS 系統規格書

## 1. 系統概述

本系統是一個完整的餐廳 POS (Point of Sale) 解決方案，提供餐廳從點餐、結帳到報表統計的全方位功能。系統採用前後端分離架構，包含員工管理界面和顧客自助點餐界面。

## 2. 系統架構

### 2.1 技術架構

- **後端**：FastAPI (Python)
- **前端**：React + Material-UI
- **資料庫**：PostgreSQL
- **身份驗證**：JWT (JSON Web Tokens)
- **緩存**：Redis (用於驗證碼和速率限制)

### 2.2 系統分層

後端採用三層架構：
- **API層**：處理HTTP請求/響應，權限驗證
- **服務層**：實現業務邏輯
- **數據層**：模型定義和數據庫操作

## 3. 用戶角色與權限

### 3.1 角色定義

- **管理員**：系統管理者，擁有全部權限
- **員工**：餐廳工作人員，根據分配的權限執行操作
- **顧客**：餐廳顧客，可進行自助點餐

### 3.2 權限系統

採用基於角色的權限控制（RBAC），主要權限領域包括：

1. **用戶管理** (`user_management`)
   - 創建用戶 (`can_create`)
   - 讀取用戶信息 (`can_read`)
   - 更新用戶 (`can_update`)
   - 刪除用戶 (`can_delete`)

2. **菜單管理** (`menu_management`)
   - 創建菜單項 (`can_create`)
   - 讀取菜單 (`can_read`)
   - 更新菜單項 (`can_update`)
   - 刪除菜單項 (`can_delete`)

3. **訂單管理** (`order_management`)
   - 創建訂單 (`can_create`)
   - 讀取訂單 (`can_read`)
   - 更新訂單 (`can_update`)
   - 刪除訂單 (`can_delete`)

4. **支付管理** (`payment_management`)
   - 處理支付 (`can_create`)
   - 查看支付記錄 (`can_read`)

5. **桌位管理** (`desk_management`)
   - 創建桌位 (`can_create`)
   - 讀取桌位信息 (`can_read`)
   - 更新桌位 (`can_update`)
   - 刪除桌位 (`can_delete`)

6. **顧客管理** (`customer_management`)
   - 創建顧客 (`can_create`)
   - 讀取顧客信息 (`can_read`)
   - 更新顧客 (`can_update`)
   - 刪除顧客 (`can_delete`)

7. **報表管理** (`report_management`)
   - 查看報表 (`can_read`)

8. **角色權限管理** (`role_management`)
   - 僅管理員可訪問

## 4. 系統功能模塊

### 4.1 認證模塊

- **員工登入**：使用用戶名和密碼
- **顧客驗證**：使用電子郵件驗證碼
- **令牌刷新**：JWT令牌到期後自動刷新
- **權限檢查**：基於用戶角色和權限的訪問控制

### 4.2 用戶管理模塊

- 創建/編輯/刪除員工
- 角色分配
- 權限查看

### 4.3 菜單管理模塊

- 創建/編輯/刪除菜單項
- 分類管理
- 價格和庫存管理

### 4.4 訂單管理模塊

- 訂單創建和處理
- 訂單狀態追踪
- 訂單歷史查詢

### 4.5 支付管理模塊

- 支付處理
- 支付記錄查詢

### 4.6 桌位管理模塊

- 桌位創建和管理
- 桌位狀態追踪
- 顧客-桌位綁定

### 4.7 報表模塊

- 日營業額報表
- 熱門商品統計

## 5. 資料模型

### 5.1 用戶相關

- `User` - 員工信息
- `Role` - 角色定義
- `Permission` - 權限定義
- `RoleUser` - 角色與用戶關聯
- `RolePermission` - 角色與權限關聯

### 5.2 顧客相關

- `Customer` - 顧客信息
- `DeskCustomer` - 桌位與顧客綁定

### 5.3 訂單相關

- `Order` - 訂單主表
- `OrderItem` - 訂單項目
- `Payment` - 支付記錄

### 5.4 菜單相關

- `MenuItem` - 菜單項目
- `Inventory` - 庫存記錄

### 5.5 桌位相關

- `Desk` - 桌位信息

## 6. API端點

### 6.1 認證API

- `POST /token/staff` - 員工登入
- `POST /custom/email-send-code` - 顧客發送驗證碼
- `POST /verify/dine-in` - 內用驗證
- `POST /verify/takeout` - 外帶驗證
- `POST /refresh/staff` - 刷新令牌
- `GET /users/me` - 獲取當前用戶信息
- `GET /users/me/permissions` - 獲取當前用戶權限

### 6.2 用戶管理API

- `GET /users/{user_uuid}` - 獲取特定用戶
- `POST /create_user/` - 創建用戶
- `DELETE /delete_user/` - 刪除用戶
- `POST /users/{user_uuid}/assign-role` - 分配角色
- `DELETE /users/{user_uuid}/remove-role` - 移除角色
- `GET /roles/` - 獲取所有角色
- `GET /permissions/` - 獲取所有權限
- `GET /users/{user_uuid}/permissions` - 獲取用戶權限

### 6.3 菜單管理API

- `GET /menu/items/` - 獲取菜單項目
- `POST /menu/items/` - 創建菜單項目
- `PUT /menu/items/{item_uuid}` - 更新菜單項目
- `DELETE /menu/items/{item_uuid}` - 刪除菜單項目
- `GET /menu/items-with-inventory/` - 獲取帶庫存信息的菜單項目

### 6.4 訂單管理API

- `GET /orders/` - 獲取訂單列表
- `POST /orders/` - 創建訂單
- `GET /orders/{order_uuid}` - 獲取特定訂單
- `PUT /orders/{order_uuid}` - 更新訂單
- `PUT /orders/{order_uuid}/status` - 更新訂單狀態

### 6.5 支付管理API

- `POST /payments/` - 處理支付
- `GET /payments/order/{order_uuid}` - 獲取訂單的支付記錄

### 6.6 桌位管理API

- `GET /desks/` - 獲取所有桌位
- `POST /desks/` - 創建桌位
- `GET /desks/{desk_uuid}` - 獲取特定桌位
- `PUT /desks/{desk_uuid}` - 更新桌位
- `DELETE /desks/delete/{desk_uuid}` - 刪除桌位
- `POST /desk-customer/` - 綁定桌位與顧客
- `GET /desk-customer/active` - 獲取活躍的桌位綁定
- `POST /desk-customer/release` - 釋放桌位綁定

### 6.7 顧客管理API

- `GET /customers/{customer_email}` - 獲取顧客
- `POST /customers/` - 創建顧客
- `PUT /customers/{customer_uuid}` - 更新顧客
- `DELETE /customers/{customer_uuid}` - 刪除顧客

### 6.8 報表API

- `GET /reports/daily-sales` - 獲取日營業額報表
- `GET /reports/popular-items` - 獲取熱門商品報表

## 7. 前端路由結構

- `/login` - 登入頁面
- `/` - 儀表板首頁
- `/customer/menu` - 顧客點餐頁面
- `/orders` - 訂單管理頁面
- `/payment/:orderId` - 支付處理頁面
- `/reports` - 報表頁面
- `/admin/*` - 管理員專用頁面
- `/unauthorized` - 權限不足頁面
- `/404` - 頁面不存在

## 8. 部署與運維

### 8.1 部署架構

- Docker容器化部署
- Nginx作為反向代理
- PostgreSQL數據庫
- Redis緩存

### 8.2 環境設置

- 開發環境
- 測試環境
- 生產環境

### 8.3 監控與日誌

- API請求日誌
- 錯誤日誌
- 性能監控

## 9. 安全考量

- JWT令牌安全
- 密碼加密存儲
- API權限控制
- 輸入驗證和sanitization
- 速率限制防止濫用

## 10. 擴展性考慮

- 可擴展的權限管理系統
- 模塊化的系統架構
- 易於添加新功能
