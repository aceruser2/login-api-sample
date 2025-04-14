# 前端啟動與使用說明

### 啟動步驟

1. 安裝依賴:
````bash
cd frontend
npm install
````

2. 開發環境啟動:
````bash
npm run dev
````
服務會在 http://localhost:3000 運行

### 前端頁面流程

#### 1. 登入頁面 (`/pages/login.tsx`)
- 提供兩種模式:
  - 外帶模式: 只需輸入電話
  - 內用模式: 需輸入電話和桌號

#### 2. 主選單頁面 (`/pages/menu.tsx`)
- 顯示所有可點餐品項
- 分類展示
- 購物車功能

#### 3. 購物車頁面 (`/pages/cart.tsx`)
- 顯示已選商品
- 修改數量
- 結帳功能

### API 串接邏輯

````typescript
export const login = async (phone: string, tableNo?: string) => {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ phone, tableNo }),
  });
  return response.json();
}
````

### 狀態管理

使用 React Context 管理:
- 用戶狀態
- 購物車狀態
- 訂單狀態

````typescript
export const AuthContext = createContext({
  isLoggedIn: false,
  userPhone: '',
  tableNo: '',
  // ...existing code...
});
````

### 開發注意事項

1. API 請求需要帶 token:
````typescript
headers: {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
}
````

2. 環境變數設定在 .env:
````plaintext
NEXT_PUBLIC_API_URL=http://localhost:8000
````

3. 路由保護使用 HOC:
````typescript
export const withAuth = (WrappedComponent: React.ComponentType) => {
  return (props: any) => {
    // ...existing code...
    return isAuthenticated ? <WrappedComponent {...props} /> : <Login />;
  };
};
````

所有需要驗證的頁面都要用 `withAuth` 包裝。