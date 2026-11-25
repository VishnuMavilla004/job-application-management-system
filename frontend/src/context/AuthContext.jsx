
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";

import { authAPI } from "../api/auth.api";
import { tokenStorage } from "../utils/tokenStorage";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const logout = useCallback(async () => {
    const refreshToken = tokenStorage.getRefreshToken();

    tokenStorage.clearTokens();
    setUser(null);

    if (refreshToken) {
      try {
        await authAPI.logout(refreshToken);
      } catch (error) {
        console.error("Server-side logout failed:", error);
      }
    }
  }, []);

  const login = async (credentials) => {
    const payload = await authAPI.login(credentials);

    const access = payload.access ?? payload.tokens?.access;
    const refresh = payload.refresh ?? payload.tokens?.refresh;

    if (!access || !refresh) {
      throw new Error("Login response did not contain both JWT tokens.");
    }

    tokenStorage.setTokens(access, refresh);

    try {
      const profile = await authAPI.getProfile();
      setUser(profile.user ?? profile);
    } catch (error) {
      tokenStorage.clearTokens();
      throw error;
    }
  };

  const register = async (userData) => {
    return authAPI.register(userData);
  };

  const refreshProfile = async () => {
    const profile = await authAPI.getProfile();
    setUser(profile.user ?? profile);
    return profile;
  };

  useEffect(() => {
    let active = true;

    const initialize = async () => {
      if (!tokenStorage.getAccessToken()) {
        if (active) setLoading(false);
        return;
      }

      try {
        const profile = await authAPI.getProfile();

        if (active) {
          setUser(profile.user ?? profile);
        }
      } catch {
        tokenStorage.clearTokens();

        if (active) {
          setUser(null);
        }
      } finally {
        if (active) setLoading(false);
      }
    };

    const handleExpired = () => {
      tokenStorage.clearTokens();
      setUser(null);
    };

    window.addEventListener("auth:expired", handleExpired);
    initialize();

    return () => {
      active = false;
      window.removeEventListener("auth:expired", handleExpired);
    };
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated: Boolean(user),
        login,
        register,
        logout,
        refreshProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider.");
  }

  return context;
}
