import React from 'react';
import { Grid, Paper, Typography, Box } from '@mui/material';
import TableRestaurantIcon from '@mui/icons-material/TableRestaurant';

export const DeskGrid = ({ desks, onDeskClick }) => {
  return (
    <Grid container spacing={2} sx={{ p: 2 }}>
      {desks.map((desk) => (
        <Grid item xs={12} sm={6} md={4} lg={3} key={desk.uuid}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              cursor: 'pointer',
              bgcolor: desk.is_occupied ? 'secondary.light' : 'background.paper',
              '&:hover': {
                bgcolor: 'action.hover',
              },
            }}
            onClick={() => onDeskClick(desk)}
          >
            <TableRestaurantIcon 
              sx={{ 
                fontSize: 40, 
                color: desk.is_occupied ? 'secondary.dark' : 'primary.main' 
              }} 
            />
            <Typography variant="h6" sx={{ mt: 1 }}>
              {desk.desk_name}
            </Typography>
            <Box sx={{ mt: 1 }}>
              <Typography variant="body2" color="text.secondary">
                {desk.is_occupied ? '使用中' : '可使用'}
              </Typography>
            </Box>
          </Paper>
        </Grid>
      ))}
    </Grid>
  );
};
