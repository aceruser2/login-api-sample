export const handleError = (error) => {
  if (error.response) {
    // API 錯誤響應
    const { status, data } = error.response;
    switch (status) {
      case 400:
        return data.detail || '請求參數錯誤';
      case 401:
        return '未授權或登入已過期';
      case 404:
        return '資源不存在';
      default:
        return data.detail || '發生未知錯誤';
    }
  }
  
  if (error.request) {
    // 請求發送失敗
    return '網路連接失敗';
  }
  
  // 其他錯誤
  return error.message || '發生未知錯誤';
};
