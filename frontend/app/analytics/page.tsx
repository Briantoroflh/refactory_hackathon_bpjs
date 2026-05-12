"use client";

import { useEffect, useState } from "react";
import { AnalyticsPage } from "@/components/analytics/analytics-page";
import { createEmptyAnalytics, fetchAnalyticsSnapshot } from "@/lib/analytics/api";
import type { TeamAnalytics } from "@/lib/analytics/types";
import AnalyticsLoading from "./loading";

export default function Page() {
  const [analytics, setAnalytics] = useState<TeamAnalytics | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    const run = async () => {
      try {
        const snapshot = await fetchAnalyticsSnapshot();
        if (!active) return;
        setAnalytics(snapshot.analytics);
        setNotice(snapshot.notice ?? null);
      } catch (error) {
        if (!active) return;
        setAnalytics(createEmptyAnalytics());
        setNotice(error instanceof Error ? error.message : "Failed to load analytics");
      }
    };

    run();
    const timer = window.setInterval(run, 30000);

    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, []);

  if (!analytics) {
    return <AnalyticsLoading />;
  }

  return <AnalyticsPage analytics={analytics} notice={notice} />;
}
