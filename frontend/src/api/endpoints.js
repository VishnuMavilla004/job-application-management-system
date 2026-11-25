
const AUTH_BASE = import.meta.env.VITE_AUTH_BASE_PATH || "auth/";

export const ENDPOINTS = {
  register: `${AUTH_BASE}register/`,
  login: `${AUTH_BASE}login/`,
  refresh: `${AUTH_BASE}refresh/`,
  logout: `${AUTH_BASE}logout/`,

  // Profile endpoint is NOT inside auth/
  profile: "users/me/",
};
