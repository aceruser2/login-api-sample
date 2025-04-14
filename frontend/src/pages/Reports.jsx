import React, { useState } from 'react';
import {
  Box,
  Paper,
  Tabs,
  Tab,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';

export const Reports = () => {
  const [tab, setTab] = useState(0);

  return (
    <Box sx={{ p: 2 }}>
      <Paper sx={{ width: '100%' }}>
        <Tabs
          value={tab}
          onChange={(e, v) => setTab(v)}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label="日營業額報表" />
          <Tab label="熱門品項統計" />
        </Tabs>

        <Box sx={{ p: 3 }}>
          {tab === 0 ? (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>日期</TableCell>
                    <TableCell align="right">訂單數</TableCell>
                    <TableCell align="right">總營業額</TableCell>
                    <TableCell align="right">平均單價</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {/* 日營業額數據 */}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>品項名稱</TableCell>
                    <TableCell align="right">銷售數量</TableCell>
                    <TableCell align="right">銷售金額</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {/* 熱門品項數據 */}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Box>
      </Paper>
    </Box>
  );
};
