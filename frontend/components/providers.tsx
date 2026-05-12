"use client";

import React from "react";
import RealtimeProviderClient from "@/lib/api/realtime";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <RealtimeProviderClient>
      {children}
    </RealtimeProviderClient>
  );
}
