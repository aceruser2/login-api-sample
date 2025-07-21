import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { CircularProgress, Box, Typography } from '@mui/material';

/**
 * 受保護的路由元件
 * @param {Object} props 
 * @param {React.ReactNode} props.children - 子元件
 * @param {string[]} [props.allowedRoles] - 允許的角色列表
 * @param {string} [props.requiredPermission] - 需要的權限
 * @param {string} [props.requiredAction] - 需要的操作權限
 * @param {boolean} [props.requireAdmin] - 是否需要管理員權限
 * @param {string} [props.redirectPath] - 重定向路徑
 */
export const ProtectedRoute = ({ 
  children, 
  allowedRoles = [],
  requiredPermission,
  requiredAction,
  requireAdmin = false,
  redirectPath = "/login" 
}) => {
  const { user, loading, initialized, hasPermission, hasRole, isAdmin } = useAuth();
  const location = useLocation();

  // 如果認證系統還在初始化, 顯示載入中
  if (!initialized || loading) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        height="100vh"
        flexDirection="column"
        gap={2}
      >
        <CircularProgress />
        <Typography>認證中...</Typography>
      </Box>
    );
  }

  // 如果沒有登入，重定向到登入頁面
  if (!user) {
    return <Navigate to={redirectPath} state={{ from: location }} replace />;
  }

  // 檢查是否有所需的角色權限
  let hasRequiredRole = true;
  if (allowedRoles.length > 0) {
    // 檢查是否有所需角色
    hasRequiredRole = allowedRoles.includes(user.userType) || 
                     allowedRoles.some(role => hasRole(role));
  }

  // 檢查是否有所需的特定權限
  let hasRequiredPermission = true;
  if (requiredPermission) {
    hasRequiredPermission = hasPermission(requiredPermission, requiredAction);
  }

  // 檢查是否需要管理員權限
  let hasAdminPermission = true;
  if (requireAdmin) {
    hasAdminPermission = isAdmin();
  }

  // 如果不符合任何權限要求，重定向到未授權頁面
  if (!hasRequiredRole || !hasRequiredPermission || !hasAdminPermission) {
    return <Navigate to="/unauthorized" replace />;
  }

  // 通過所有檢查，渲染子元件
  return children;
};

export default ProtectedRoute;
