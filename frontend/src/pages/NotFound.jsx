import React from 'react';
import { Box, Typography, Button, Paper } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';

export const NotFound = () => {
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
        <ErrorOutlineIcon sx={{ fontSize: 60, color: 'warning.main', mb: 2 }} />
        
        <Typography variant="h4" gutterBottom>
          頁面不存在
        </Typography>
        
        <Typography variant="body1" paragraph sx={{ mb: 3 }}>
          您訪問的頁面不存在或已被移除。請檢查URL或返回首頁。
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

export default NotFound;
