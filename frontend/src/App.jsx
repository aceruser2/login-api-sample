import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { theme } from './theme';

// 頁面
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { OrderPage } from './pages/OrderPage';
import { OrderManagement } from './pages/OrderManagement';
import { PaymentPage } from './pages/PaymentPage';
import { Reports } from './pages/Reports';
import { NotFound } from './pages/NotFound';
import { Unauthorized } from './pages/Unauthorized';
import { ScanQRLogin } from './pages/ScanQRLogin';

// 組件
import { Layout } from './components/Layout';
import { ProtectedRoute } from './components/Auth/ProtectedRoute';

// 上下文
import { AuthProvider } from './contexts/AuthContext';
import { LoadingProvider } from './contexts/LoadingContext';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <LoadingProvider>
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              {/* 公開路由 */}
              <Route path="/login" element={<Login />} />
              <Route path="/unauthorized" element={<Unauthorized />} />
              
              {/* 基本用戶頁面 */}
              <Route path="/" element={
                <ProtectedRoute>
                  <Layout>
                    <Dashboard />
                  </Layout>
                </ProtectedRoute>
              } />
              
              {/* 顧客點餐頁面 */}
              <Route path="/customer/menu" element={
                <ProtectedRoute allowedRoles={['customer']}>
                  <Layout>
                    <OrderPage />
                  </Layout>
                </ProtectedRoute>
              } />
              
              {/* 訂單管理 (需要 order_management 權限) */}
              <Route path="/orders" element={
                <ProtectedRoute 
                  allowedRoles={['staff']}
                  requiredPermission="order_management"
                  requiredAction="can_read"
                >
                  <Layout>
                    <OrderManagement />
                  </Layout>
                </ProtectedRoute>
              } />
              
              {/* 支付處理 (需要 payment_management 權限) */}
              <Route path="/payment/:orderId" element={
                <ProtectedRoute 
                  allowedRoles={['staff']}
                  requiredPermission="payment_management"
                  requiredAction="can_create"
                >
                  <Layout>
                    <PaymentPage />
                  </Layout>
                </ProtectedRoute>
              } />
              
              {/* 報表頁面 (需要 report_management 權限) */}
              <Route path="/reports" element={
                <ProtectedRoute 
                  allowedRoles={['staff']}
                  requiredPermission="report_management"
                  requiredAction="can_read"
                >
                  <Layout>
                    <Reports />
                  </Layout>
                </ProtectedRoute>
              } />
              
              {/* 管理員專用頁面 */}
              <Route path="/admin/*" element={
                <ProtectedRoute requireAdmin={true}>
                  <Layout>
                    {/* 管理員頁面內容，如果需要可以再加子路由 */}
                    <Dashboard />
                  </Layout>
                </ProtectedRoute>
              } />
              
              {/* 二維碼掃描登入頁面 */}
              <Route path="/scan-login" element={<ScanQRLogin />} />
              
              {/* 404頁面 */}
              <Route path="/404" element={<NotFound />} />
              
              {/* 未匹配路由重定向到登入頁 */}
              <Route path="*" element={<Navigate to="/404" />} />
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </LoadingProvider>
    </ThemeProvider>
  );
}

export default App;
