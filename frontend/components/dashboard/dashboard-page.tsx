"use client";

import { useCallback, useEffect, useState } from "react";
import { DashboardShell } from "./dashboard-shell";
import { DashboardSkeleton } from "./dashboard-skeletons";
import { fetchDashboardOverview } from "@/lib/dashboard/api";
import type { DashboardOverview } from "@/lib/dashboard/types";
import { AppLayout } from "@/components/layout/app-layout";

const emptyOverview: DashboardOverview = {
  generatedAt: new Date().toISOString(),
  profile: {
    name: "Dashboard",
    title: "Realtime overview",
    projects: 0,
    team: 0,
  },
  stats: [],
  sprint: {
    title: "Active Work Progress",
    subtitle: "Waiting for live data",
    bars: [],
  },
  notifications: [],
  activities: [],
};

function normalizeOverview(data: Partial<DashboardOverview>): DashboardOverview {
  return {
    generatedAt: data.generatedAt ?? emptyOverview.generatedAt,
    profile: data.profile ?? emptyOverview.profile,
    stats: data.stats ?? emptyOverview.stats,
    sprint: data.sprint ?? emptyOverview.sprint,
    notifications: data.notifications ?? emptyOverview.notifications,
    activities: data.activities ?? emptyOverview.activities,
  };
}

export function DashboardPage() {
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadOverview = useCallback(async () => {
    try {
      const data = await fetchDashboardOverview();
      setOverview(normalizeOverview(data));
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load dashboard data");
    }
  }, []);

  useEffect(() => {
    let active = true;

    const run = async () => {
      try {
        const data = await fetchDashboardOverview();
        if (!active) return;
        setOverview(normalizeOverview(data));
        setError(null);
      } catch (err) {
        if (!active) return;
        setError(err instanceof Error ? err.message : "Failed to load dashboard data");
      }
    };

    run();
    const timer = window.setInterval(run, 30000);

    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, []);

  if (!overview) {
    if (!error) {
      return <DashboardSkeleton />;
    }

    return (
      <AppLayout title="Dashboard Overview">
        <div className="rounded-[24px] border border-rose-200 bg-white p-6 text-slate-700 shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
          <p className="text-[18px] font-semibold text-slate-800">Gagal memuat dashboard</p>
          <p className="mt-2 text-[14px] leading-6 text-slate-500">{error}</p>
          <button
            type="button"
            onClick={loadOverview}
            className="mt-5 rounded-2xl bg-[#3f2fd6] px-4 py-3 text-[14px] font-semibold text-white"
          >
            Coba lagi
          </button>
        </div>
      </AppLayout>
    );
  }

  return <DashboardShell overview={overview} />;
}
