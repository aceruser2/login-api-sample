import api from '../utils/api';

// 認證相關API
export const authService = {
  // 員工登入
  staffLogin: (username, password) => 
    api.post('/token/staff', { username, password }),
  
  // 顧客發送驗證碼
  customerSendCode: (data) => 
    api.post('/custom/email-send-code', data),
    
  // 內用驗證
  verifyDineIn: (data) => 
    api.post('/verify/dine-in', data),

  // 外帶驗證
  verifyTakeout: (data) => 
    api.post('/verify/takeout', data),

  // 刷新令牌
  refreshToken: (refreshToken) => 
    api.post('/refresh/staff', {}, {
      headers: { Authorization: `Bearer ${refreshToken}` }
    }),

  // 獲取當前用戶信息
  getCurrentUser: () => 
    api.get('/users/me'),
    
  // 獲取當前用戶的權限
  getCurrentUserPermissions: () =>
    api.get('/users/me/permissions')
};

// 用戶管理相關API
export const userService = {
  // 獲取所有用戶
  getAllUsers: (skip = 0, limit = 20) =>
    api.get(`/users/?skip=${skip}&limit=${limit}`),
    
  // 獲取特定用戶
  getUserById: (uuid) =>
    api.get(`/users/${uuid}`),
    
  // 創建用戶
  createUser: (userData) =>
    api.post('/create_user/', {}, { params: userData }),
    
  // 刪除用戶
  deleteUser: (userUuid) =>
    api.delete(`/delete_user/?user_uuid=${userUuid}`),

  // 獲取所有角色
  getAllRoles: () =>
    api.get('/roles/'),
    
  // 獲取所有權限
  getAllPermissions: () =>
    api.get('/permissions/'),
    
  // 分配角色給用戶
  assignRoleToUser: (userUuid, roleUuid) =>
    api.post(`/users/${userUuid}/assign-role?role_uuid=${roleUuid}`),
    
  // 移除用戶的角色
  removeRoleFromUser: (userUuid, roleUuid) =>
    api.delete(`/users/${userUuid}/remove-role?role_uuid=${roleUuid}`),
    
  // 獲取用戶的權限
  getUserPermissions: (userUuid) =>
    api.get(`/users/${userUuid}/permissions`)
};

// 桌位管理相關API
export const deskService = {
  // 獲取所有桌位
  getAllDesks: (skip = 0, limit = 100) => 
    api.get(`/desks/?skip=${skip}&limit=${limit}`),
    
  // 獲取特定桌位
  getDeskById: (uuid) => 
    api.get(`/desks/${uuid}`),
    
  // 創建桌位
  createDesk: (deskData) => 
    api.post('/desks/', deskData),
    
  // 更新桌位
  updateDesk: (uuid, deskData) =>
    api.put(`/desks/${uuid}`, deskData),
    
  // 刪除桌位
  deleteDesk: (uuid) =>
    api.delete(`/desks/delete/${uuid}`),
    
  // 綁定桌位與顧客
  bindDesk: (customerEmail, deskUuid) => 
    api.post('/desk-customer/', { customer_email: customerEmail, desk_uuid: deskUuid }),
    
  // 獲取活躍的桌位綁定
  getActiveBinding: (customerEmail) =>
    api.get(`/desk-customer/active?customer_email=${customerEmail}`),
    
  // 釋放桌位綁定
  releaseBinding: (customerEmail) =>
    api.post('/desk-customer/release', { customer_email: customerEmail })
};

// 訂單相關API
export const orderService = {
  // 創建訂單
  createOrder: (data) => 
    api.post('/orders/', data),
    
  // 獲取訂單列表
  getOrders: (skip = 0, limit = 20, statusFilter = null) => {
    let url = `/orders/?skip=${skip}&limit=${limit}`;
    if (statusFilter !== null) url += `&status_filter=${statusFilter}`;
    return api.get(url);
  },
    
  // 獲取特定訂單
  getOrderById: (orderId) =>
    api.get(`/orders/${orderId}`),
    
  // 更新訂單
  updateOrder: (orderId, orderData) =>
    api.put(`/orders/${orderId}`, orderData),
    
  // 更新訂單狀態
  updateOrderStatus: (orderId, status) => 
    api.put(`/orders/${orderId}/status`, { status })
};

// 支付相關API
export const paymentService = {
  // 處理支付
  processPayment: (data) => 
    api.post('/payments/', data),
    
  // 獲取訂單的支付記錄
  getPaymentsByOrder: (orderUuid) =>
    api.get(`/payments/order/${orderUuid}`)
};

// 菜單相關API
export const menuService = {
  // 獲取菜單項目
  getMenuItems: (skip = 0, limit = 20, category = null) => {
    let url = `/menu/items/?skip=${skip}&limit=${limit}`;
    if (category) url += `&category=${category}`;
    return api.get(url);
  },
  
  // 獲取包含庫存信息的菜單項目
  getMenuItemsWithInventory: (skip = 0, limit = 20, category = null) => {
    let url = `/menu/items-with-inventory/?skip=${skip}&limit=${limit}`;
    if (category) url += `&category=${category}`;
    return api.get(url);
  },
  
  // 創建菜單項目
  createMenuItem: (data) => 
    api.post('/menu/items/', data),
  
  // 更新菜單項目
  updateMenuItem: (uuid, data) => 
    api.put(`/menu/items/${uuid}`, data),
  
  // 刪除菜單項目
  deleteMenuItem: (uuid) => 
    api.delete(`/menu/items/${uuid}`)
};

// 報表相關API
export const reportService = {
  // 獲取日營業額報表
  getDailySales: (date = null) => {
    let url = '/reports/daily-sales';
    if (date) url += `?date=${date.toISOString()}`;
    return api.get(url);
  },
  
  // 獲取熱門商品報表
  getPopularItems: (days = 7) => 
    api.get(`/reports/popular-items?days=${days}`),
};

// 顧客相關API
export const customerService = {
  // 通過郵箱獲取顧客
  getCustomerByEmail: (email) =>
    api.get(`/customers/${email}`),
    
  // 創建顧客
  createCustomer: (customerData) =>
    api.post('/customers/', customerData),
    
  // 更新顧客
  updateCustomer: (uuid, customerData) =>
    api.put(`/customers/${uuid}`, customerData),
    
  // 刪除顧客
  deleteCustomer: (uuid) =>
    api.delete(`/customers/${uuid}`)
};
