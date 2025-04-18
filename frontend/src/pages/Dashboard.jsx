import React from "react";
import { Typography, Box } from "@mui/material";

export const Dashboard = () => (
  <Box sx={{ p: 3 }}>
    <Typography variant="h4" gutterBottom>
      Dashboard
    </Typography>
    <Typography color="text.secondary">
      歡迎使用餐廳 POS 系統！
    </Typography>
  </Box>
);
