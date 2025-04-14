import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Box,
  Chip
} from '@mui/material';
import { Order } from '../types';
import { getOrders, updateOrderStatus } from '../api/orders';

export const OrderManagement = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  
  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {
    const data = await getOrders();
    setOrders(data);
  };

  const handleStatusChange = async (orderId: string, newStatus: string) => {
    await updateOrderStatus(orderId, newStatus);
    loadOrders();
  };

  return (
    <Container>
      <Typography variant="h4" gutterBottom>
        Order Management
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Order ID</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Total</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {orders.map((order) => (
              <TableRow key={order.uuid}>
                <TableCell>{order.uuid}</TableCell>
                <TableCell>{order.order_type}</TableCell>
                <TableCell>
                  <Chip 
                    label={order.status}
                    color={order.status === 'completed' ? 'success' : 'default'}
                  />
                </TableCell>
                <TableCell>${order.total_amount}</TableCell>
                <TableCell>{/* Status change actions */}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
};
