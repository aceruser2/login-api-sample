import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import RestaurantIcon from '@mui/icons-material/Restaurant';

export const Header = ({ user, onLogout }) => {
  return (
    <AppBar position="static">
      <Toolbar>
        <RestaurantIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          餐廳 POS 系統
        </Typography>
        {user && (
          <Box>
            <Typography variant="subtitle2" sx={{ mr: 2 }}>
              {user.username || user.customer_name}
            </Typography>
            <Button color="inherit" onClick={onLogout}>
              登出
            </Button>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
};
