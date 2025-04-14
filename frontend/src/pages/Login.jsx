import React, { useState } from 'react';
import {
  Box,
  Paper,
  Tabs,
  Tab,
  TextField,
  Button,
  Typography,
  Container
} from '@mui/material';
import { LoadingButton } from '@mui/lab';

export const Login = () => {
  const [tab, setTab] = useState(0);
  const [loading, setLoading] = useState(false);

  const handleStaffLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    // 員工登入邏輯
  };

  const handleCustomerLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    // 顧客登入邏輯
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
            <Tab label="顧客登入" />
          </Tabs>

          {tab === 0 ? (
            <Box component="form" onSubmit={handleStaffLogin}>
              <TextField
                fullWidth
                label="帳號"
                margin="normal"
                name="username"
                required
              />
              <TextField
                fullWidth
                label="密碼"
                type="password"
                margin="normal"
                name="password"
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
                name="name"
                required
              />
              <TextField
                fullWidth
                label="電話"
                margin="normal"
                name="phone"
                required
              />
              <TextField
                fullWidth
                label="桌號"
                margin="normal"
                name="desk"
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
          )}
        </Paper>
      </Box>
    </Container>
  );
};
