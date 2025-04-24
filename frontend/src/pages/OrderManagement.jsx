import React, { useState } from 'react';
import {
  Box,
  Paper,
  Grid,
  Typography,
  List,
  ListItem,
  ListItemText,
  Divider,
  Button,
  Chip
} from '@mui/material';

export const OrderManagement = () => {
  const [selectedOrder, setSelectedOrder] = useState(null);

  return (
    <Grid container spacing={2} sx={{ p: 2 }}>
      <Grid item xs={12} md={4}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            進行中訂單
          </Typography>
          <List>
            {/* 訂單列表 */}
            <ListItemButton 
              selected={selectedOrder?.id === 1}
              onClick={() => setSelectedOrder({ id: 1 })}
            >
              <ListItemText 
                primary="訂單 #001" 
                secondary="桌號: A1 | 金額: $500"
              />
              <Chip label="製作中" color="primary" size="small" />
            </ListItemButton>
            <Divider />
          </List>
        </Paper>
      </Grid>
      
      <Grid item xs={12} md={8}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            訂單詳情
          </Typography>
          {selectedOrder ? (
            <Box>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="subtitle1">
                    訂單項目
                  </Typography>
                  <List>
                    {/* 訂單項目列表 */}
                  </List>
                </Grid>
                <Grid item xs={12}>
                  <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
                    <Button variant="outlined" color="secondary">
                      取消訂單
                    </Button>
                    <Button variant="contained" color="primary">
                      完成訂單
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </Box>
          ) : (
            <Typography color="text.secondary">
              請選擇一個訂單查看詳情
            </Typography>
          )}
        </Paper>
      </Grid>
    </Grid>
  );
};
