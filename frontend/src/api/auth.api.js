
import api from "./axios";
import { ENDPOINTS } from "./endpoints";

export const authAPI = {
  async login(credentials) {
    const response = await api.post(ENDPOINTS.login, credentials);
    return response.data?.data ?? response.data;
  },

  async register(userData) {
    const response = await api.post(ENDPOINTS.register, userData);
    return response.data?.data ?? response.data;
  },

  async getProfile() {
    const response = await api.get(ENDPOINTS.profile);
    return response.data?.data ?? response.data;
  },

  async logout(refreshToken) {
    const response = await api.post(ENDPOINTS.logout, {
      refresh: refreshToken,
    });

    return response.data;
  },
};
