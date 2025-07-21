import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../utils/api';
import { handleError } from '../utils/errorHandler';

// 創建認證上下文
const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  // 用戶信息狀態
  const [user, setUser] = useState(null);
  // 用戶角色狀態
  const [roles, setRoles] = useState([]);
  // 用戶權限狀態
  const [permissions, setPermissions] = useState([]);
  // 載入狀態
  const [loading, setLoading] = useState(true);
  // 初始化完成狀態
  const [initialized, setInitialized] = useState(false);

  // 初始化: 檢查存儲中的令牌並嘗試獲取用戶信息
  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        setLoading(false);
        setInitialized(true);
        return;
      }

      try {
        // 獲取當前用戶信息
        const response = await api.get('/users/me');
        const userInfo = response;
        
        // 獲取用戶類型
        const userType = localStorage.getItem('userType');
        
        // 如果是員工, 還要獲取角色和權限
        if (userType === 'staff') {
          try {
            // 獲取當前用戶的權限信息
            const permissionsResponse = await api.get('/users/me/permissions');
            // 存儲角色和權限信息
            setRoles(permissionsResponse.roles || []);
            setPermissions(permissionsResponse.permissions || []);
            
            // 同時保存到本地存儲，用於頁面刷新時快速恢復
            localStorage.setItem('userRoles', JSON.stringify(permissionsResponse.roles || []));
            localStorage.setItem('userPermissions', JSON.stringify(permissionsResponse.permissions || []));
          } catch (error) {
            console.error('Failed to fetch permissions:', error);
            
            // 嘗試從本地存儲恢復角色和權限信息
            const storedRoles = JSON.parse(localStorage.getItem('userRoles') || '[]');
            const storedPermissions = JSON.parse(localStorage.getItem('userPermissions') || '[]');
            setRoles(storedRoles);
            setPermissions(storedPermissions);
          }
        }
        
        setUser({ ...userInfo, userType });
      } catch (error) {
        console.error('Auth initialization failed:', error);
        // 清除令牌和相關信息
        logout();
      } finally {
        setLoading(false);
        setInitialized(true);
      }
    };

    initializeAuth();
  }, []);

  // 員工登入函數
  const staffLogin = async (username, password) => {
    setLoading(true);
    try {
      // 員工登入請求
      const response = await api.post('/token/staff', { username, password });
      
      // 存儲令牌
      localStorage.setItem('token', response.access_token);
      localStorage.setItem('refreshToken', response.refresh_token);
      localStorage.setItem('userType', 'staff');
      
      // 獲取用戶信息
      const userResponse = await api.get('/users/me');
      const userInfo = { ...userResponse, userType: 'staff' };
      
      // 存儲角色和權限信息
      const rolesData = response.roles || [];
      const permissionsData = response.permissions || [];
      
      setUser(userInfo);
      setRoles(rolesData);
      setPermissions(permissionsData);
      
      // 保存到本地存儲
      localStorage.setItem('userRoles', JSON.stringify(rolesData));
      localStorage.setItem('userPermissions', JSON.stringify(permissionsData));
      
      return { user: userInfo, roles: rolesData, permissions: permissionsData };
    } catch (error) {
      const errorMsg = handleError(error);
      throw new Error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  // 顧客登入函數 - 完成驗證後的處理
  const customerLogin = async (verifyResponse) => {
    setLoading(true);
    try {
      // 存儲令牌
      localStorage.setItem('token', verifyResponse.access_token);
      localStorage.setItem('refreshToken', verifyResponse.refresh_token || '');
      localStorage.setItem('userType', 'customer');
      
      // 獲取用戶信息
      const userResponse = await api.get('/users/me');
      const userInfo = { ...userResponse, userType: 'customer' };
      
      setUser(userInfo);
      // 顧客沒有角色和權限
      setRoles([]);
      setPermissions([]);
      
      return { user: userInfo };
    } catch (error) {
      const errorMsg = handleError(error);
      throw new Error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  // 登出函數
  const logout = () => {
    // 清除所有令牌和用戶信息
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('userType');
    localStorage.removeItem('customerEmail');
    localStorage.removeItem('deskNumber');
    localStorage.removeItem('userRoles');
    localStorage.removeItem('userPermissions');
    
    // 清除狀態
    setUser(null);
    setRoles([]);
    setPermissions([]);
  };

  // 檢查是否有特定權限
  const hasPermission = (permissionName, actionType = null) => {
    if (!user || user.userType !== 'staff') return false;
    
    // 找到對應權限
    const permission = permissions.find(p => p.permission_name === permissionName);
    if (!permission) return false;
    
    // 如果沒有指定動作類型, 只檢查是否有該權限
    if (!actionType) return true;
    
    // 檢查是否有執行特定動作的權限
    return permission.attributes && permission.attributes[actionType] === true;
  };

  // 檢查是否有特定角色
  const hasRole = (roleName) => {
    if (!user || user.userType !== 'staff') return false;
    return roles.some(role => role.role_name.toLowerCase() === roleName.toLowerCase());
  };

  // 檢查是否是管理員
  const isAdmin = () => {
    if (!user || user.userType !== 'staff') return false;
    return roles.some(role => role.role_name.toLowerCase() === 'admin' && role.level >= 9);
  };

  // 提供的上下文值
  const value = {
    user,
    roles,
    permissions,
    loading,
    initialized,
    staffLogin,
    customerLogin,
    logout,
    hasPermission,
    hasRole,
    isAdmin
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// 使用認證上下文的hook
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
