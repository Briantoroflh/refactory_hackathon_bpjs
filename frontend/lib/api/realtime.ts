"use client";

import React, { createContext, useContext, useEffect, useRef, useState } from "react";

type RealtimeMessage = any;

type RealtimeContextShape = {
  subscribe: (cb: (msg: RealtimeMessage) => void) => () => void;
  lastMessage: RealtimeMessage | null;
  connected: boolean;
};

const RealtimeContext = createContext<RealtimeContextShape>({
  subscribe: () => () => {},
  lastMessage: null,
  connected: false,
});

export function useRealtime() {
  return useContext(RealtimeContext);
}

export function RealtimeProviderClient({ children }: { children: React.ReactNode }) {
  const wsRef = useRef<WebSocket | null>(null);
  const subscribersRef = useRef<Set<(m: RealtimeMessage) => void>>(new Set());
  const reconnectTimer = useRef<number | null>(null);
  const [lastMessage, setLastMessage] = useState<RealtimeMessage | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const wsUrl = base.replace(/^http/, "ws") + "/ws";
    let shouldStop = false;
    let backoff = 1000;

    const connect = () => {
      try {
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          backoff = 1000;
          setConnected(true);
        };

        ws.onmessage = (ev) => {
          try {
            const msg = JSON.parse(ev.data);
            setLastMessage(msg);
            subscribersRef.current.forEach((cb) => cb(msg));
          } catch (e) {
            // ignore parsing errors
          }
        };

        ws.onclose = () => {
          setConnected(false);
          if (!shouldStop) {
            reconnectTimer.current = window.setTimeout(() => connect(), backoff);
            backoff = Math.min(backoff * 1.5, 20000);
          }
        };

        ws.onerror = () => {
          // close and let onclose handle reconnect
          ws.close();
        };
      } catch (e) {
        if (!shouldStop) {
          reconnectTimer.current = window.setTimeout(() => connect(), backoff);
          backoff = Math.min(backoff * 1.5, 20000);
        }
      }
    };

    connect();

    return () => {
      shouldStop = true;
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current);
      }
      try {
        wsRef.current?.close();
      } catch (e) {}
      subscribersRef.current.clear();
    };
  }, []);

  const subscribe = (cb: (m: RealtimeMessage) => void) => {
    subscribersRef.current.add(cb);
    return () => subscribersRef.current.delete(cb);
  };

  const value: RealtimeContextShape = {
    subscribe,
    lastMessage,
    connected,
  };

  return <RealtimeContext.Provider value={value}>{children}</RealtimeContext.Provider>;
}

export default RealtimeProviderClient;
