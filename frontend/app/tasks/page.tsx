"use client";

import { useEffect, useState } from "react";
import { TasksPage } from "@/components/tasks/tasks-page";
import { createEmptyTaskBoard, fetchTaskBoardSnapshot } from "@/lib/tasks/api";
import type { SprintTasks } from "@/lib/tasks/types";
import TasksLoading from "./loading";

export default function Page() {
  const [tasks, setTasks] = useState<SprintTasks | null>(null);
  const [projectId, setProjectId] = useState<number>(3);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    const run = async () => {
      try {
        const snapshot = await fetchTaskBoardSnapshot();
        if (!active) return;
        setTasks(snapshot.board);
        setProjectId(snapshot.projectId);
        setNotice(snapshot.notice ?? null);
      } catch (err) {
        if (!active) return;
        setTasks(createEmptyTaskBoard());
        setNotice(err instanceof Error ? err.message : "Failed to load tasks");
      }
    };

    run();
    const timer = window.setInterval(run, 30000);

    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, []);

  if (!tasks) {
    return <TasksLoading />;
  }

  return <TasksPage tasks={tasks} projectId={projectId} notice={notice} />;
}
