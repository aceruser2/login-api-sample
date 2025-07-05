import React, { useState, useEffect } from 'react';
import {
  Container, Typography, Grid, Card, CardContent, CardMedia, 
  Button, Box, TextField, Snackbar, Alert, Divider, List,
  ListItem, ListItemText, Dialog, DialogTitle, DialogContent,
  DialogActions, FormControl, InputLabel, Select, MenuItem
} from '@mui/material';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const OrderPage = () => {
  // 狀態管理
  const [menuItems, setMenuItems] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [cart, setCart] = useState([]);
  const [alert, setAlert] = useState({ open: false, message: '', severity: 'info' });
  const [loading, setLoading] = useState(true);
  const [checkoutDialog, setCheckoutDialog] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState('cash');
  
  // 獲取令牌和顧客信息
  const token = localStorage.getItem('token');
  const userType = localStorage.getItem('userType');
  const deskNumber = localStorage.getItem('deskNumber');
  const customerEmail = localStorage.getItem('customerEmail');
  
  // 加載菜單項目
  useEffect(() => {
    const fetchMenuItems = async () => {
      try {
        // 設置請求頭，包含授權令牌
        const headers = { Authorization: `Bearer ${token}` };
        // 使用新端點獲取帶庫存信息的菜單項目
        const response = await axios.get(`${API_URL}/menu/items-with-inventory/`, { headers });
        
        setMenuItems(response.data);
        
        // 提取唯一類別
        const uniqueCategories = [...new Set(response.data.map(item => item.category))];
        setCategories(uniqueCategories);
        
        setLoading(false);
      } catch (error) {
        console.error('加載菜單失敗：', error);
        showAlert('加載菜單失敗', 'error');
        setLoading(false);
      }
    };
    
    if (token) {
      fetchMenuItems();
    } else {
      // 未登入，跳轉到登入頁面
      window.location.href = '/login';
    }
  }, [token]);
  
  // 顯示提醒訊息
  const showAlert = (message, severity = 'error') => {
    setAlert({ open: true, message, severity });
  };
  
  // 添加商品到購物車
  const addToCart = (item) => {
    // 檢查庫存是否足夠
    if (!item.available || item.stock_quantity <= 0) {
      showAlert(`${item.name} 已售罄`, 'error');
      return;
    }
    
    const existingItem = cart.find(cartItem => cartItem.uuid === item.uuid);
    const currentQuantity = existingItem ? existingItem.quantity : 0;
    
    // 檢查購物車數量是否超過庫存
    if (currentQuantity + 1 > item.stock_quantity) {
      showAlert(`${item.name} 庫存不足，剩餘 ${item.stock_quantity} 份`, 'warning');
      return;
    }
    
    if (existingItem) {
      // 如果商品已在購物車中，增加數量
      setCart(cart.map(cartItem => 
        cartItem.uuid === item.uuid 
          ? { ...cartItem, quantity: cartItem.quantity + 1, subtotal: (cartItem.quantity + 1) * cartItem.price } 
          : cartItem
      ));
    } else {
      // 否則添加新商品
      setCart([...cart, { 
        ...item, 
        quantity: 1,
        subtotal: item.price
      }]);
    }
    
    showAlert(`已添加 ${item.name} 到購物車`, 'success');
  };
  
  // 從購物車移除商品
  const removeFromCart = (itemUuid) => {
    setCart(cart.filter(item => item.uuid !== itemUuid));
  };
  
  // 更新購物車中商品數量
  const updateQuantity = (itemUuid, newQuantity) => {
    if (newQuantity < 1) return;
    
    setCart(cart.map(item => 
      item.uuid === itemUuid 
        ? { ...item, quantity: newQuantity, subtotal: newQuantity * item.price } 
        : item
    ));
  };
  
  // 計算總金額
  const calculateTotal = () => {
    return cart.reduce((sum, item) => sum + item.subtotal, 0);
  };
  
  // 提交訂單
  const submitOrder = async () => {
    if (cart.length === 0) {
      showAlert('購物車不能為空', 'error');
      return;
    }
    
    setLoading(true);
    
    try {
      // 設置請求頭，包含授權令牌
      const headers = { Authorization: `Bearer ${token}` };
      
      // 準備訂單數據
      const orderData = {
        customer_uuid: localStorage.getItem('customerUuid') || customerEmail,
        desk_uuid: userType === 'customer' && deskNumber ? deskNumber : null,
        order_type: userType === 'customer' && deskNumber ? 'dine_in' : 'takeout',
        items: cart.map(item => ({
          item_uuid: item.uuid,
          quantity: item.quantity,
          note: item.note || ''
        })),
        note: ''
      };
      
      // 提交訂單
      const orderResponse = await axios.post(`${API_URL}/orders/`, orderData, { headers });
      
      if (orderResponse.status === 200) {
        // 如果訂單創建成功，進行結帳
        const paymentData = {
          order_uuid: orderResponse.data.uuid,
          payment_method: paymentMethod,
          amount_paid: calculateTotal(),
          payment_note: ''
        };
        
        const paymentResponse = await axios.post(`${API_URL}/payments/`, paymentData, { headers });
        
        if (paymentResponse.status === 200) {
          // 清空購物車並關閉結帳對話框
          setCart([]);
          setCheckoutDialog(false);
          showAlert('訂單提交並付款成功！', 'success');
          
          // 如果是內用訂單，桌位綁定會在支付服務中自動釋放
          if (userType === 'customer' && deskNumber) {
            localStorage.removeItem('deskNumber');
          }
        }
      }
      
    } catch (error) {
      console.error('訂單提交失敗：', error);
      const errorMessage = error.response?.data?.detail || '訂單提交失敗';
      showAlert(errorMessage, 'error');
    } finally {
      setLoading(false);
    }
  };
  
  // 過濾菜單項目
  const filteredMenuItems = selectedCategory === 'all' 
    ? menuItems 
    : menuItems.filter(item => item.category === selectedCategory);

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" gutterBottom>
          {userType === 'customer' && deskNumber ? '內用點餐' : '外帶點餐'}
        </Typography>
        
        {/* 類別選擇 */}
        <Box sx={{ mb: 3 }}>
          <Button 
            variant={selectedCategory === 'all' ? 'contained' : 'outlined'}
            onClick={() => setSelectedCategory('all')}
            sx={{ mr: 1, mb: 1 }}
          >
            全部
          </Button>
          {categories.map(category => (
            <Button
              key={category}
              variant={selectedCategory === category ? 'contained' : 'outlined'}
              onClick={() => setSelectedCategory(category)}
              sx={{ mr: 1, mb: 1 }}
            >
              {category}
            </Button>
          ))}
        </Box>
        
        <Grid container spacing={3}>
          {/* 菜單項目 */}
          <Grid item xs={12} md={8}>
            <Grid container spacing={2}>
              {loading ? (
                <Typography>載入中...</Typography>
              ) : (
                filteredMenuItems.map(item => (
                  <Grid item xs={12} sm={6} md={4} key={item.uuid}>
                    <Card>
                      {item.image_url && (
                        <CardMedia
                          component="img"
                          height="140"
                          image={item.image_url}
                          alt={item.name}
                        />
                      )}
                      <CardContent>
                        <Typography variant="h6">{item.name}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {item.description}
                        </Typography>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
                          <Typography variant="h6">${item.price}</Typography>
                          {/* 添加庫存顯示 */}
                          <Typography variant="caption" color={item.stock_quantity > 0 ? 'text.secondary' : 'error'}>
                            {item.stock_quantity > 0 ? `庫存: ${item.stock_quantity}` : '已售罄'}
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                          <Button 
                            variant="contained" 
                            size="small"
                            onClick={() => addToCart(item)}
                            disabled={!item.available || item.stock_quantity <= 0}
                          >
                            加入
                          </Button>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                ))
              )}
            </Grid>
          </Grid>
          
          {/* 購物車 */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h5" gutterBottom>
                  購物車
                </Typography>
                
                {cart.length === 0 ? (
                  <Typography>購物車是空的</Typography>
                ) : (
                  <>
                    <List>
                      {cart.map(item => (
                        <React.Fragment key={item.uuid}>
                          <ListItem>
                            <ListItemText 
                              primary={item.name} 
                              secondary={`$${item.price} × ${item.quantity} = $${item.subtotal}`} 
                            />
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              <Button 
                                size="small"
                                onClick={() => updateQuantity(item.uuid, item.quantity - 1)}
                              >
                                -
                              </Button>
                              <Typography sx={{ mx: 1 }}>{item.quantity}</Typography>
                              <Button 
                                size="small"
                                onClick={() => updateQuantity(item.uuid, item.quantity + 1)}
                              >
                                +
                              </Button>
                              <Button 
                                size="small"
                                color="error"
                                onClick={() => removeFromCart(item.uuid)}
                              >
                                移除
                              </Button>
                            </Box>
                          </ListItem>
                          <Divider />
                        </React.Fragment>
                      ))}
                    </List>
                    
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="h6">
                        總計: ${calculateTotal()}
                      </Typography>
                      <Button 
                        variant="contained" 
                        color="primary" 
                        fullWidth 
                        sx={{ mt: 2 }}
                        disabled={cart.length === 0}
                        onClick={() => setCheckoutDialog(true)}
                      >
                        結帳
                      </Button>
                    </Box>
                  </>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
      
      {/* 結帳對話框 */}
      <Dialog open={checkoutDialog} onClose={() => setCheckoutDialog(false)}>
        <DialogTitle>確認訂單</DialogTitle>
        <DialogContent>
          <Typography gutterBottom>訂單總計: ${calculateTotal()}</Typography>
          
          <FormControl fullWidth margin="normal">
            <InputLabel>支付方式</InputLabel>
            <Select
              value={paymentMethod}
              onChange={(e) => setPaymentMethod(e.target.value)}
              label="支付方式"
            >
              <MenuItem value="cash">現金</MenuItem>
              <MenuItem value="credit_card">信用卡</MenuItem>
              <MenuItem value="mobile_payment">行動支付</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCheckoutDialog(false)}>取消</Button>
          <Button 
            variant="contained" 
            onClick={submitOrder} 
            disabled={loading}
          >
            {loading ? '處理中...' : '確認支付'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* 提醒訊息 */}
      <Snackbar 
        open={alert.open} 
        autoHideDuration={6000} 
        onClose={() => setAlert({ ...alert, open: false })}
      >
        <Alert onClose={() => setAlert({ ...alert, open: false })} severity={alert.severity}>
          {alert.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};
