
const ACCESS_TOKEN_KEY = "jam_access_token";
const REFRESH_TOKEN_KEY = "jam_refresh_token";

export const tokenStorage = {
  getAccessToken() {
    return sessionStorage.getItem(ACCESS_TOKEN_KEY);
  },

  getRefreshToken() {
    return sessionStorage.getItem(REFRESH_TOKEN_KEY);
  },

  setTokens(access, refresh) {
    sessionStorage.setItem(ACCESS_TOKEN_KEY, access);
    sessionStorage.setItem(REFRESH_TOKEN_KEY, refresh);
  },

  clearTokens() {
    sessionStorage.removeItem(ACCESS_TOKEN_KEY);
    sessionStorage.removeItem(REFRESH_TOKEN_KEY);
  },
};
