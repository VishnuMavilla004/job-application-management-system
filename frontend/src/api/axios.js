
import axios from "axios";
import { tokenStorage } from "../utils/tokenStorage";
import { ENDPOINTS } from "./endpoints";

const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL ||
    "http://127.0.0.1:8000/api/v1/"



const api = axios.create({
    baseURL:
        import.meta.env.VITE_API_BASE_URL ||
        "http://127.0.0.1:8000/api/v1/",
});


const refreshClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

let refreshPromise = null;

// Attach access token to outgoing requests.
api.interceptors.request.use((config) => {
  const accessToken = tokenStorage.getAccessToken();

  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }

  return config;
});

api.interceptors.request.use((config) => {
  const accessToken = tokenStorage.getAccessToken();

  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }

  // Allow the browser to set multipart/form-data and its boundary.
  if (
    typeof FormData !== "undefined" &&
    config.data instanceof FormData
  ) {
    config.headers.delete("Content-Type");
  }

  return config;
});

// Handle expired access tokens.
api.interceptors.response.use(
  (response) => response,

  async (error) => {
    const originalRequest = error.config;

    if (
      error.response?.status !== 401 ||
      !originalRequest ||
      originalRequest._retry ||
      originalRequest.url?.includes(ENDPOINTS.refresh) ||
      originalRequest.url?.includes(ENDPOINTS.login)
    ) {
      return Promise.reject(error);
    }

    const refreshToken = tokenStorage.getRefreshToken();

    if (!refreshToken) {
      tokenStorage.clearTokens();
      window.dispatchEvent(new Event("auth:expired"));
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    try {
      if (!refreshPromise) {
        refreshPromise = refreshClient
          .post(ENDPOINTS.refresh, {
            refresh: refreshToken,
          })
          .then((response) => {
            const payload = response.data?.data ?? response.data;
            const access = payload.access;

            if (!access) {
              throw new Error(
                "Refresh response did not contain an access token."
              );
            }

            tokenStorage.setTokens(
              access,
              payload.refresh || refreshToken
            );

            return access;
          })
          .finally(() => {
            refreshPromise = null;
          });
      }

      const newAccessToken = await refreshPromise;

      originalRequest.headers.Authorization =
        `Bearer ${newAccessToken}`;

      return api(originalRequest);
    } catch (refreshError) {
      tokenStorage.clearTokens();
      window.dispatchEvent(new Event("auth:expired"));

      return Promise.reject(refreshError);
    }
  }
);

export default api;
