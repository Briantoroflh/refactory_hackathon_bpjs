import { useState, useCallback } from "react";
import { apiClient } from "./client";
import type { LoginFormValues } from "@/lib/auth/validation";

export type UserResponse = {
  user_id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
  last_login?: string;
};

export type LoginResponseDTO = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: UserResponse;
};

export type RegisterRequest = {
  email: string;
  password: string;
  full_name?: string;
};

export type TokenRefreshRequest = {
  refresh_token: string;
};

export const authAPI = {
  login: (data: LoginFormValues) =>
    apiClient.post<LoginResponseDTO>("/auth/login", data),

  register: (data: RegisterRequest) =>
    apiClient.post<LoginResponseDTO>("/auth/register", data),

  refresh: (data: TokenRefreshRequest) =>
    apiClient.post<LoginResponseDTO>("/auth/refresh", data),

  logout: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    }
  },

  getCurrentUser: () => apiClient.get<UserResponse>("/auth/me"),
};

export type UseAuthState = {
  user: UserResponse | null;
  loading: boolean;
  error: Error | null;
  isAuthenticated: boolean;
};

export function useAuth() {
  const [state, setState] = useState<UseAuthState>({
    user: null,
    loading: false,
    error: null,
    isAuthenticated: false,
  });

  const getCurrentUser = useCallback(async () => {
    setState((s) => ({ ...s, loading: true, error: null }));
    try {
      const token =
        typeof window !== "undefined"
          ? localStorage.getItem("access_token")
          : null;

      if (!token) {
        setState((s) => ({
          ...s,
          user: null,
          loading: false,
          isAuthenticated: false,
        }));
        return null;
      }

      const user = await authAPI.getCurrentUser();
      setState((s) => ({
        ...s,
        user,
        loading: false,
        isAuthenticated: true,
      }));
      return user;
    } catch (error) {
      const err = error instanceof Error ? error : new Error(String(error));
      setState((s) => ({
        ...s,
        user: null,
        loading: false,
        error: err,
        isAuthenticated: false,
      }));
      return null;
    }
  }, []);

  const logout = useCallback(() => {
    authAPI.logout();
    setState({
      user: null,
      loading: false,
      error: null,
      isAuthenticated: false,
    });
  }, []);

  return {
    ...state,
    getCurrentUser,
    logout,
  };
}

export function useLazyLogin() {
  const [state, setState] = useState<{
    data: LoginResponseDTO | null;
    loading: boolean;
    error: Error | null;
  }>({
    data: null,
    loading: false,
    error: null,
  });

  const launch = useCallback(async (credentials: LoginFormValues) => {
    setState({ data: null, loading: true, error: null });
    try {
      const response = await authAPI.login(credentials);
      setState({ data: response, loading: false, error: null });
      return response;
    } catch (error) {
      const err = error instanceof Error ? error : new Error(String(error));
      setState({ data: null, loading: false, error: err });
      throw err;
    }
  }, []);

  return {
    ...state,
    launch,
  };
}

export function useLazyRegister() {
  const [state, setState] = useState<{
    data: LoginResponseDTO | null;
    loading: boolean;
    error: Error | null;
  }>({
    data: null,
    loading: false,
    error: null,
  });

  const launch = useCallback(async (data: RegisterRequest) => {
    setState({ data: null, loading: true, error: null });
    try {
      const response = await authAPI.register(data);
      setState({ data: response, loading: false, error: null });
      return response;
    } catch (error) {
      const err = error instanceof Error ? error : new Error(String(error));
      setState({ data: null, loading: false, error: err });
      throw err;
    }
  }, []);

  return {
    ...state,
    launch,
  };
}
