export type ApiEnvelope<T> = {
  status: string;
  message: string;
  data: T;
};

export type ProfileUser = {
  user_id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
  last_login?: string;
};

class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ??
  "http://localhost:8000";

const AUTH_STORAGE_KEY =
  process.env.NEXT_PUBLIC_AUTH_STORAGE_KEY ?? "access_token";

function getAccessToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  return localStorage.getItem(AUTH_STORAGE_KEY);
}

function decodeUserIdFromToken(token: string): number | null {
  try {
    const parts = token.split(".");
    if (parts.length < 2) {
      return null;
    }

    const base64 = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const padded = base64.padEnd(Math.ceil(base64.length / 4) * 4, "=");
    const payload = JSON.parse(atob(padded)) as { sub?: string };

    if (!payload.sub) {
      return null;
    }

    const parsed = Number(payload.sub);
    return Number.isFinite(parsed) ? parsed : null;
  } catch {
    return null;
  }
}

function unwrapEnvelope<T>(payload: unknown): T {
  if (
    typeof payload === "object" &&
    payload !== null &&
    "status" in payload &&
    "data" in payload
  ) {
    return (payload as ApiEnvelope<T>).data;
  }

  return payload as T;
}

async function readErrorMessage(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as {
      message?: string;
      detail?: string;
      data?: Array<{ msg?: string }> | string;
    };

    if (Array.isArray(payload.data) && payload.data.length > 0) {
      return (
        payload.data[0]?.msg ??
        payload.message ??
        payload.detail ??
        "Request failed"
      );
    }

    return payload.message ?? payload.detail ?? "Request failed";
  } catch {
    return `Request failed (${response.status})`;
  }
}

async function requestWithAuth<T>(
  endpoint: string,
  options?: RequestInit,
): Promise<T> {
  const token = getAccessToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options?.headers as Record<string, string> | undefined),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
    credentials: "include",
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new ApiError(message, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const payload = await response.json();
  return unwrapEnvelope<T>(payload);
}

export async function fetchCurrentProfile(): Promise<ProfileUser> {
  const token = getAccessToken();

  if (!token) {
    throw new Error("Not authenticated");
  }

  try {
    return await requestWithAuth<ProfileUser>("/auth/me");
  } catch (error) {
    const canFallback =
      error instanceof ApiError &&
      (error.status === 401 || error.status === 404 || error.status === 405);

    if (!canFallback) {
      throw error;
    }

    const userId = decodeUserIdFromToken(token);
    if (!userId) {
      throw new Error("Unable to resolve user id from access token");
    }

    return requestWithAuth<ProfileUser>(`/users/${userId}`);
  }
}

export async function updateCurrentProfile(data: {
  full_name: string;
}): Promise<ProfileUser> {
  const token = getAccessToken();

  if (!token) {
    throw new Error("Not authenticated");
  }

  const userId = decodeUserIdFromToken(token);

  if (!userId) {
    throw new Error("Unable to resolve user id from access token");
  }

  return requestWithAuth<ProfileUser>(`/users/${userId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}
