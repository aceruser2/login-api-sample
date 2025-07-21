import React from 'react';
import { Box, Typography, Button, Paper } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import LockIcon from '@mui/icons-material/Lock';

export const Unauthorized = () => {
  const navigate = useNavigate();
  
  return (
    <Box 
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        p: 2
      }}
    >
      <Paper
        sx={{
          p: 4,
          maxWidth: 500,
          textAlign: 'center',
          borderRadius: 2
        }}
        elevation={3}
      >
        <LockIcon sx={{ fontSize: 60, color: 'error.main', mb: 2 }} />
        
        <Typography variant="h4" gutterBottom sx={{ color: 'error.main' }}>
          權限不足
        </Typography>
        
        <Typography variant="body1" paragraph sx={{ mb: 3 }}>
          您沒有訪問此頁面的權限。請聯絡系統管理員或返回首頁。
        </Typography>
        
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
          <Button 
            variant="contained" 
            color="primary"
            onClick={() => navigate('/')}
          >
            返回首頁
          </Button>
          
          <Button 
            variant="outlined"
            onClick={() => navigate(-1)}
          >
            返回上一頁
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default Unauthorized;
