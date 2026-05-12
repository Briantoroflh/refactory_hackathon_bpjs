import type { LoginFormValues } from "./validation";

export type LoginRequest = {
  email: string;
  password: string;
  rememberMe: boolean;
};

export type LoginResponse = {
  accessToken: string;
  refreshToken?: string;
  user?: {
    id: string;
    name: string;
    role: string;
  };
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

export async function login(values: LoginFormValues): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(values as LoginRequest),
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  return (await response.json()) as LoginResponse;
}

async function readErrorMessage(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: string; message?: string };
    return payload.detail ?? payload.message ?? "Unable to sign in.";
  } catch {
    return "Unable to sign in.";
  }
}
