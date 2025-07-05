import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const authApi = {
  /**
   * 員工登入
   * @param {string} username - 員工帳號
   * @param {string} password - 員工密碼
   * @returns {Promise<object>} 包含JWT令牌的響應
   */
  login: async (username, password) => {
    const response = await axios.post(`${API_URL}/token/staff`, {
      username,
      password,
      userstatus: 0
    });
    return response.data;
  },

  /**
   * 顧客登入請求發送驗證碼
   * @param {object} customerData - 顧客資料
   * @param {string} customerData.custom_name - 顧客姓名
   * @param {string} customerData.email - 顧客電子郵件
   * @param {string} customerData.phone - 顧客電話
   * @returns {Promise<object>} 發送結果
   */
  customerLogin: async (customerData) => {
    const response = await axios.post(`${API_URL}/custom/email-send-code`, customerData);
    return response.data;
  },

  /**
   * 內用顧客驗證碼確認並綁定桌位
   * @param {object} loginData - 登入資料
   * @param {string} loginData.email - 顧客電子郵件
   * @param {string} loginData.phone - 顧客電話
   * @param {string} loginData.custom_name - 顧客姓名
   * @param {string} verificationCode - 驗證碼
   * @param {string} deskUuid - 桌位UUID
   * @returns {Promise<object>} 包含JWT令牌的響應
   */
  verifyDineIn: async (loginData, verificationCode, deskUuid) => {
    const response = await axios.post(`${API_URL}/verify/dine-in`, {
      email: loginData.email,
      verify_code: verificationCode,
      desk_uuid: deskUuid
    });
    return response.data;
  },
  
  /**
   * 外帶顧客驗證碼確認
   * @param {object} loginData - 登入資料
   * @param {string} loginData.email - 顧客電子郵件
   * @param {string} loginData.phone - 顧客電話
   * @param {string} verificationCode - 驗證碼
   * @returns {Promise<object>} 包含JWT令牌的響應
   */
  verifyTakeout: async (loginData, verificationCode) => {
    const response = await axios.post(`${API_URL}/verify/takeout`, {
      email: loginData.email,
      verify_code: verificationCode
    });
    return response.data;
  },
  
  /**
   * 獲取顧客活躍的桌位綁定
   * @param {string} email - 顧客電子郵件
   * @returns {Promise<object>} 桌位綁定資訊
   */
  getActiveBinding: async (email) => {
    const response = await axios.get(`${API_URL}/desk-customer/active?customer_email=${email}`);
    return response.data;
  },
  
  /**
   * 釋放顧客的桌位綁定
   * @param {string} email - 顧客電子郵件
   * @returns {Promise<object>} 釋放結果
   */
  releaseBinding: async (email) => {
    const response = await axios.post(`${API_URL}/desk-customer/release`, {
      customer_email: email
    });
    return response.data;
  },

  /**
   * 員工為顧客綁定桌位
   */
  bindDeskByStaff: async (customerEmail, deskUuid) => {
    const token = localStorage.getItem('token');
    const response = await axios.post(`${API_URL}/desk-customer/`, {
      customer_email: customerEmail,
      desk_uuid: deskUuid
    }, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.data;
  },

  /**
   * 員工處理支付
   */
  processPayment: async (paymentData) => {
    const token = localStorage.getItem('token');
    const response = await axios.post(`${API_URL}/payments/`, paymentData, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.data;
  },
};
