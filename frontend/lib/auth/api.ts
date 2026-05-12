import type { LoginFormValues } from "./validation";
import { clearStoredAuthToken, getStoredAuthToken, setStoredAuthToken } from "./storage";

export type LoginRequest = {
  email: string;
  password: string;
  rememberMe?: boolean;
};

// Backend wrapped response format (API wraps all responses)
export type BackendWrappedResponse<T> = {
  status: string;
  message: string;
  data: T;
};

// Backend login data format
export type BackendLoginData = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: {
    user_id: number;
    email: string;
    full_name?: string;
    is_active: boolean;
    last_login?: string;
  };
};

// Frontend response format (normalized)
export type LoginResponse = {
  access_token: string;
  refresh_token: string;
  user: {
    id: number;
    email: string;
    name?: string;
  };
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ??
  "http://localhost:8000";

export async function login(values: LoginFormValues): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email: values.email,
      password: values.password,
    }),
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  // Backend wraps response in {status, message, data}
  const wrappedResponse =
    (await response.json()) as BackendWrappedResponse<BackendLoginData>;
  const backendData = wrappedResponse.data;

  // Store token in localStorage
  if (typeof window !== "undefined") {
    setStoredAuthToken(backendData.access_token);
    if (backendData.refresh_token) {
      localStorage.setItem("refresh_token", backendData.refresh_token);
    }
  }

  // Return normalized response
  return {
    access_token: backendData.access_token,
    refresh_token: backendData.refresh_token,
    user: {
      id: backendData.user.user_id,
      email: backendData.user.email,
      name: backendData.user.full_name,
    },
  };
}

export function logout(): void {
  if (typeof window !== "undefined") {
    clearStoredAuthToken();
    localStorage.removeItem("refresh_token");
  }
}

export function getStoredToken(): string | null {
  return getStoredAuthToken();
}

export function isAuthenticated(): boolean {
  return getStoredToken() !== null;
}

async function readErrorMessage(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as {
      status?: string;
      message?: string;
      detail?: string;
      data?: Array<{ msg?: string; message?: string }> | string;
    };

    // Handle wrapped error format with validation errors
    if (
      payload.data &&
      Array.isArray(payload.data) &&
      payload.data.length > 0
    ) {
      const firstError = payload.data[0];
      return (
        firstError.msg ??
        firstError.message ??
        payload.message ??
        "Unable to sign in."
      );
    }

    // Handle direct error response
    return payload.message ?? payload.detail ?? "Unable to sign in.";
  } catch {
    return "Unable to sign in.";
  }
}
