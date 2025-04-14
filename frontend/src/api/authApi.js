import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const authApi = {
  login: async (username, password) => {
    const response = await axios.post(`${API_URL}/token/user`, {
      username,
      password,
      userstatus: 0
    });
    return response.data;
  },

  customerLogin: async (customerData) => {
    const response = await axios.post(`${API_URL}/token/dine-in`, customerData);
    return response.data;
  },

  verifyDineIn: async (loginData, verificationCode) => {
    const response = await axios.post(`${API_URL}/verify/dine-in`, {
      ...loginData,
      verification_code: verificationCode
    });
    return response.data;
  }
};
