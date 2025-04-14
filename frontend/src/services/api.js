import api from '../utils/api';

export const authService = {
  login: (username, password) => 
    api.post('/token/user', { username, password, userstatus: 0 }),
  
  customerLogin: (data) => 
    api.post('/token/dine-in', data),
    
  verifyDineIn: (data, code) => 
    api.post('/verify/dine-in', { ...data, verification_code: code })
};

export const deskService = {
  getAllDesks: (skip = 0, limit = 10) => 
    api.get(`/desks/?skip=${skip}&limit=${limit}`),
    
  getDeskById: (uuid) => 
    api.get(`/desk/${uuid}`),
    
  createDesk: (deskName) => 
    api.post('/desk/create', { desk_name: deskName }),
    
  bindDesk: (customerPhone, deskUuid) => 
    api.post('/desk-customer/', { customer_phone: customerPhone, desk_uuid: deskUuid })
};

export const orderService = {
  createOrder: (data) => 
    api.post('/orders/', data),
    
  updateOrderStatus: (orderId, status) => 
    api.put(`/orders/${orderId}/status`, { status }),
    
  getOrdersByCustomer: () => 
    api.get('/orders/customer')
};

export const paymentService = {
  processPayment: (data) => 
    api.post('/payments/', data)
};
