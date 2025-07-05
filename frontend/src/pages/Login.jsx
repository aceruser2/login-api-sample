import React, { useState } from 'react';
import {
  Box,
  Paper,
  Tabs,
  Tab,
  TextField,
  Button,
  Typography,
  Container,
  Snackbar,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import { LoadingButton } from '@mui/lab';
import { authApi } from '../api/authApi';

export const Login = () => {
  // 基本狀態
  const [tab, setTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [alert, setAlert] = useState({ open: false, message: '', severity: 'info' });
  
  // 員工登入狀態
  const [staffCredentials, setStaffCredentials] = useState({
    username: '',
    password: ''
  });
  
  // 顧客登入狀態
  const [customerInfo, setCustomerInfo] = useState({
    custom_name: '',
    phone: '',
    email: '',
  });
  
  // 驗證碼狀態
  const [verificationState, setVerificationState] = useState({
    showDialog: false,
    code: '',
    deskNumber: '',
    isTakeout: false,
  });

  // 員工輸入變更處理
  const handleStaffInputChange = (e) => {
    const { name, value } = e.target;
    setStaffCredentials({ ...staffCredentials, [name]: value });
  };

  // 顧客輸入變更處理
  const handleCustomerInputChange = (e) => {
    const { name, value } = e.target;
    setCustomerInfo({ ...customerInfo, [name]: value });
  };

  // 顯示提醒訊息
  const showAlert = (message, severity = 'error') => {
    setAlert({ open: true, message, severity });
  };

  // 員工登入處理
  const handleStaffLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const { username, password } = staffCredentials;
      if (!username || !password) {
        showAlert('請輸入帳號和密碼');
        return;
      }
      
      const result = await authApi.login(username, password);
      // 儲存令牌和用戶類型
      localStorage.setItem('token', result.access_token);
      localStorage.setItem('refreshToken', result.refresh_token);
      localStorage.setItem('userType', 'staff');
      
      showAlert('登入成功！', 'success');
      // 員工導向管理儀表板
      setTimeout(() => {
        window.location.href = '/staff/dashboard';
      }, 1500);
    } catch (error) {
      console.error('登入失敗：', error);
      showAlert(error.response?.data?.detail || '登入失敗，請檢查帳號密碼');
    } finally {
      setLoading(false);
    }
  };

  // 顧客登入處理 - 發送驗證碼
  const handleCustomerLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const { custom_name, phone, email } = customerInfo;
      
      // 驗證輸入
      if (!custom_name || !phone || !email) {
        showAlert('請填寫所有欄位');
        return;
      }
      
      // 發送驗證碼請求
      await authApi.customerLogin(customerInfo);
      
      // 成功後打開驗證碼對話框
      setVerificationState({
        ...verificationState,
        showDialog: true,
        isTakeout: tab === 2  // tab=2 表示外帶登入
      });
      
      showAlert('驗證碼已發送至您的郵箱', 'success');
    } catch (error) {
      console.error('發送驗證碼失敗：', error);
      showAlert(error.response?.data?.detail || '發送驗證碼失敗');
    } finally {
      setLoading(false);
    }
  };

  // 驗證碼確認處理
  const handleVerifyCode = async () => {
    setLoading(true);
    
    try {
      const { code, deskNumber, isTakeout } = verificationState;
      
      if (!code) {
        showAlert('請輸入驗證碼');
        return;
      }
      
      let result;
      if (isTakeout) {
        // 外帶驗證
        result = await authApi.verifyTakeout(customerInfo, code);
      } else {
        // 內用驗證，需要桌號
        if (!deskNumber) {
          showAlert('請輸入桌號');
          return;
        }
        result = await authApi.verifyDineIn(customerInfo, code, deskNumber);
      }
      
      // 儲存令牌和用戶類型
      localStorage.setItem('token', result.access_token);
      localStorage.setItem('refreshToken', result.refresh_token);
      localStorage.setItem('userType', 'customer');
      localStorage.setItem('customerEmail', customerInfo.email);
      
      // 如果是內用，還要儲存桌號
      if (!isTakeout) {
        localStorage.setItem('deskNumber', deskNumber);
      }
      
      setVerificationState({ ...verificationState, showDialog: false });
      showAlert('登入成功！', 'success');
      
      // 顧客導向點餐頁面
      setTimeout(() => {
        window.location.href = isTakeout ? '/customer/takeout-menu' : '/customer/menu';
      }, 1500);
    } catch (error) {
      console.error('驗證失敗：', error);
      showAlert(error.response?.data?.detail || '驗證碼錯誤或已過期');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h5" align="center" gutterBottom>
            餐廳 POS 系統
          </Typography>
          <Tabs value={tab} onChange={(e, v) => setTab(v)} centered sx={{ mb: 3 }}>
            <Tab label="員工登入" />
            <Tab label="內用登入" />
            <Tab label="外帶登入" />
          </Tabs>

          {tab === 0 ? (
            <Box component="form" onSubmit={handleStaffLogin}>
              <TextField
                fullWidth
                label="帳號"
                margin="normal"
                name="username"
                value={staffCredentials.username}
                onChange={handleStaffInputChange}
                required
              />
              <TextField
                fullWidth
                label="密碼"
                type="password"
                margin="normal"
                name="password"
                value={staffCredentials.password}
                onChange={handleStaffInputChange}
                required
              />
              <LoadingButton
                loading={loading}
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3 }}
              >
                登入
              </LoadingButton>
            </Box>
          ) : (
            <Box component="form" onSubmit={handleCustomerLogin}>
              <TextField
                fullWidth
                label="姓名"
                margin="normal"
                name="custom_name"
                value={customerInfo.custom_name}
                onChange={handleCustomerInputChange}
                required
              />
              <TextField
                fullWidth
                label="電話"
                margin="normal"
                name="phone"
                value={customerInfo.phone}
                onChange={handleCustomerInputChange}
                required
              />
              <TextField
                fullWidth
                label="電子郵件"
                margin="normal"
                name="email"
                type="email"
                value={customerInfo.email}
                onChange={handleCustomerInputChange}
                required
              />
              <LoadingButton
                loading={loading}
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3 }}
              >
                發送驗證碼
              </LoadingButton>
            </Box>
          )}
        </Paper>
      </Box>
      
      {/* 驗證碼對話框 */}
      <Dialog open={verificationState.showDialog} onClose={() => setVerificationState({ ...verificationState, showDialog: false })}>
        <DialogTitle>請輸入驗證碼</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="驗證碼"
            fullWidth
            value={verificationState.code}
            onChange={(e) => setVerificationState({ ...verificationState, code: e.target.value })}
          />
          {!verificationState.isTakeout && (
            <TextField
              margin="dense"
              label="桌號"
              fullWidth
              value={verificationState.deskNumber}
              onChange={(e) => setVerificationState({ ...verificationState, deskNumber: e.target.value })}
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setVerificationState({ ...verificationState, showDialog: false })}>
            取消
          </Button>
          <LoadingButton loading={loading} onClick={handleVerifyCode}>
            確認
          </LoadingButton>
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
