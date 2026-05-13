"use client";

import { useEffect, useState } from "react";
import { TeamPage } from "@/components/team/team-page";
import { createEmptyTeamAccessControl, fetchTeamAccessControl } from "@/lib/team/api";
import type { TeamAccessControl } from "@/lib/team/types";
import Loading from "./loading";

export default function Page() {
  const [accessControl, setAccessControl] = useState<TeamAccessControl | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    const run = async () => {
      try {
        const snapshot = await fetchTeamAccessControl();
        if (!active) return;
        setAccessControl(snapshot);
        setNotice(snapshot.notice ?? null);
      } catch (error) {
        if (!active) return;
        setAccessControl(createEmptyTeamAccessControl());
        setNotice(error instanceof Error ? error.message : "Failed to load team data");
      }
    };

    run();
    const timer = window.setInterval(run, 30000);

    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, []);

  if (!accessControl) {
    return <Loading />;
  }

  return <TeamPage accessControl={accessControl} notice={notice} />;
}
