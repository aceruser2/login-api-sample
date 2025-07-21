/**
 * 處理API錯誤並返回用戶友好的錯誤訊息
 * @param {Error} error - Axios錯誤對象
 * @returns {string} 友好錯誤訊息
 */
export const handleError = (error) => {
  if (error.response) {
    // API 錯誤響應
    const { status, data } = error.response;
    switch (status) {
      case 400:
        return data.detail || '請求參數錯誤';
      case 401:
        return '未授權或登入已過期';
      case 403:
        return '您沒有執行此操作的權限';
      case 404:
        return '資源不存在';
      case 422:
        return '輸入資料驗證失敗';
      case 500:
        return '伺服器內部錯誤，請稍後再試';
      default:
        return data.detail || '發生未知錯誤';
    }
  }
  
  if (error.request) {
    // 請求發送失敗
    return '網路連接失敗，請檢查您的網路連接';
  }
  
  // 其他錯誤
  return error.message || '發生未知錯誤';
};

/**
 * 格式化API錯誤訊息，用於表單錯誤
 * @param {Object} errors - 錯誤對象
 * @returns {Object} 格式化後的錯誤訊息
 */
export const formatErrors = (errors) => {
  if (!errors || typeof errors !== 'object') return {};
  
  // 處理FastAPI ValidationError格式的錯誤
  if (errors.detail && Array.isArray(errors.detail)) {
    const formattedErrors = {};
    errors.detail.forEach(err => {
      // 提取欄位名稱 (通常是loc陣列的最後一個元素)
      const fieldName = err.loc[err.loc.length - 1];
      formattedErrors[fieldName] = err.msg;
    });
    return formattedErrors;
  }
  
  return errors;
};
