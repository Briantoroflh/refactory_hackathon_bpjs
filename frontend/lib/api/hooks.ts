"use client";

import { useState, useEffect, useCallback } from "react";
import { getStoredAuthToken } from "@/lib/auth/storage";

type ApiEnvelope<T> = {
  status: string;
  message: string;
  data: T;
};

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

export interface UseAsyncState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

export function useAsync<T>(
  asyncFunction: () => Promise<T>,
  immediate = true,
  dependencies: React.DependencyList = [],
  pollInterval = 0,
): UseAsyncState<T> & { refetch: () => Promise<void> } {
  const [state, setState] = useState<UseAsyncState<T>>({
    data: null,
    loading: immediate,
    error: null,
  });

  const execute = useCallback(async () => {
    setState({ data: null, loading: true, error: null });
    try {
      const response = await asyncFunction();
      setState({ data: response, loading: false, error: null });
    } catch (error) {
      setState({
        data: null,
        loading: false,
        error: error instanceof Error ? error : new Error("Unknown error"),
      });
    }
  }, dependencies);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [immediate, execute]);

  // Setup polling if pollInterval is provided
  useEffect(() => {
    if (pollInterval > 0 && immediate) {
      const interval = setInterval(execute, pollInterval);
      return () => clearInterval(interval);
    }
  }, [pollInterval, immediate, execute]);

  return {
    ...state,
    refetch: execute,
  };
}

export function useFetch<T>(
  url: string,
  options?: RequestInit & { immediate?: boolean; refetchInterval?: number },
) {
  const {
    immediate = true,
    refetchInterval = 0,
    ...fetchOptions
  } = options || {};
  const [state, setState] = useState<UseAsyncState<T>>({
    data: null,
    loading: immediate,
    error: null,
  });

  const fetch = useCallback(async () => {
    setState({ data: null, loading: true, error: null });
    try {
      const token = getStoredAuthToken();
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };

      // Merge existing headers
      if (fetchOptions.headers) {
        const existingHeaders = fetchOptions.headers;
        if (existingHeaders instanceof Headers) {
          existingHeaders.forEach((value, key) => {
            headers[key] = value;
          });
        } else if (Array.isArray(existingHeaders)) {
          existingHeaders.forEach(([key, value]) => {
            headers[key] = value;
          });
        } else {
          Object.assign(headers, existingHeaders);
        }
      }

      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      const response = await window.fetch(url, {
        ...fetchOptions,
        headers,
        credentials: "include",
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.message || error.detail || `API error: ${response.status}`);
      }

      if (response.status === 204) {
        setState({ data: null as T, loading: false, error: null });
        return;
      }

      const data = await response.json();
      setState({ data: unwrapEnvelope<T>(data), loading: false, error: null });
    } catch (error) {
      setState({
        data: null,
        loading: false,
        error: error instanceof Error ? error : new Error("Unknown error"),
      });
    }
  }, [url, fetchOptions]);

  useEffect(() => {
    if (immediate) {
      fetch();
    }
  }, [immediate, fetch]);

  useEffect(() => {
    if (refetchInterval > 0) {
      const interval = setInterval(fetch, refetchInterval);
      return () => clearInterval(interval);
    }
  }, [fetch, refetchInterval]);

  return {
    ...state,
    refetch: fetch,
  };
}
