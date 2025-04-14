import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid
} from '@mui/material';

export const PaymentPage = () => {
  const [paymentMethod, setPaymentMethod] = useState('');
  const [amount, setAmount] = useState('');

  const handlePayment = () => {
    // 處理支付邏輯
  };

  return (
    <Box sx={{ p: 2 }}>
      <Paper sx={{ p: 3, maxWidth: 600, mx: 'auto' }}>
        <Typography variant="h5" gutterBottom>
          訂單結帳
        </Typography>
        
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="subtitle1">
              訂單編號: #001
            </Typography>
            <Typography variant="subtitle1">
              應付金額: $500
            </Typography>
          </Grid>

          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>支付方式</InputLabel>
              <Select
                value={paymentMethod}
                onChange={(e) => setPaymentMethod(e.target.value)}
              >
                <MenuItem value="cash">現金</MenuItem>
                <MenuItem value="credit_card">信用卡</MenuItem>
                <MenuItem value="line_pay">Line Pay</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="實收金額"
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
            />
          </Grid>

          <Grid item xs={12}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
              <Button variant="outlined" color="secondary">
                取消
              </Button>
              <Button
                variant="contained"
                color="primary"
                onClick={handlePayment}
              >
                確認支付
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};
