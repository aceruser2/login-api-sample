import React from 'react';
import { useAuth } from '../../contexts/AuthContext';

/**
 * 權限控制元件 - 根據權限顯示或隱藏內容
 * 
 * @param {string} permissionName - 所需權限名稱
 * @param {string} action - 所需操作權限 (can_create, can_read, can_update, can_delete)
 * @param {string} roleName - 所需角色名稱
 * @param {boolean} requireAdmin - 是否需要管理員權限
 * @param {React.ReactNode} children - 子元件
 * @param {React.ReactNode} fallback - 無權限時顯示的內容
 * @returns {React.ReactNode}
 */
export const PermissionGuard = ({
  permissionName,
  action,
  roleName,
  requireAdmin = false,
  children,
  fallback = null
}) => {
  const { hasPermission, hasRole, isAdmin } = useAuth();
  
  // 權限檢查邏輯
  const hasAccess = () => {
    // 需要管理員權限
    if (requireAdmin && !isAdmin()) return false;
    
    // 需要特定角色
    if (roleName && !hasRole(roleName)) return false;
    
    // 需要特定權限
    if (permissionName && !hasPermission(permissionName, action)) return false;
    
    // 通過所有檢查
    return true;
  };
  
  // 根據權限決定是否顯示內容
  return hasAccess() ? children : fallback;
};

export default PermissionGuard;
