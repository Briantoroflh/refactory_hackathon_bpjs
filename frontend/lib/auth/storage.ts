const AUTH_STORAGE_KEY =
  process.env.NEXT_PUBLIC_AUTH_STORAGE_KEY ?? "access_token";

export function getAuthStorageKey(): string {
  return AUTH_STORAGE_KEY;
}

export function getStoredAuthToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  return localStorage.getItem(AUTH_STORAGE_KEY);
}

export function setStoredAuthToken(token: string): void {
  if (typeof window === "undefined") {
    return;
  }

  localStorage.setItem(AUTH_STORAGE_KEY, token);
}

export function clearStoredAuthToken(): void {
  if (typeof window === "undefined") {
    return;
  }

  localStorage.removeItem(AUTH_STORAGE_KEY);
}
