"use client";

import dynamic from "next/dynamic";
import { useCallback, useEffect, useMemo, useState } from "react";
import { AppLayout } from "@/components/layout/app-layout";
import { createSprintTask, fetchSprintBoardData, sprintSidebarItems, updateTaskStatus } from "@/lib/sprints/api";
import { moveTaskToStatus } from "@/lib/sprints/board";
import {
  createMembersMap,
  filterTasks,
  getDueDateState,
  getSprintPointSummary,
  getSprintProgress,
  groupTasksByStatus,
} from "@/lib/sprints/selectors";
import type { SprintBoardData, SprintFilterState, SprintTaskStatus } from "@/lib/sprints/types";
import { SprintSkeleton } from "./sprint-skeleton";

// Lazy load heavy components
const KanbanBoard = dynamic(() => import("./kanban-board").then(mod => mod.KanbanBoard), {
  loading: () => <div className="h-[400px] animate-pulse rounded-3xl bg-slate-100" />,
  ssr: false
});

const CreateTaskModal = dynamic(() => import("./create-task-modal").then(mod => mod.CreateTaskModal), {
  ssr: false
});

const SprintOverview = dynamic(() => import("./sprint-statistics").then(mod => mod.SprintOverview), {
  loading: () => <div className="h-[200px] animate-pulse rounded-[24px] bg-slate-100" />,
  ssr: false
});

const SprintStatCards = dynamic(() => import("./sprint-statistics").then(mod => mod.SprintStatCards), {
  loading: () => <div className="h-[300px] animate-pulse rounded-[24px] bg-slate-100" />,
  ssr: false
});

const SprintEmptyState = dynamic(() => import("./sprint-empty-state").then(mod => mod.SprintEmptyState), {
  ssr: false
});

const defaultFilters: SprintFilterState = {
  query: "",
  priority: "all",
  assigneeId: "all",
};

export function SprintPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [boardData, setBoardData] = useState<SprintBoardData | null>(null);
  const [filters, setFilters] = useState<SprintFilterState>(defaultFilters);
  const [draggingTaskId, setDraggingTaskId] = useState<string | null>(null);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreatingSprint, setIsCreatingSprint] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const projectId = 3;

  const loadBoardData = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await fetchSprintBoardData(projectId);
      setBoardData(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load sprint data");
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    let active = true;

    const run = async () => {
      try {
        const data = await fetchSprintBoardData(projectId);
        if (!active) return;
        setBoardData(data);
        setError(null);
      } catch (err) {
        if (!active) return;
        setError(err instanceof Error ? err.message : "Failed to load sprint data");
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    };

    run();
    const timer = window.setInterval(run, 30000);

    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, [projectId]);

  const data = boardData ?? {
    sprint: {
      id: "loading",
      name: "Loading sprint...",
      projectPath: ["Sprints"],
      startDateLabel: "",
      endDateLabel: "",
      daysRemaining: 0,
      storyPointGoal: 0,
    },
    members: [],
    stats: [],
    tasks: [],
    sidebarItems: sprintSidebarItems,
    velocity: [],
    insights: {
      title: "AI Standup Insight",
      subtitle: "Waiting for live data",
      summary: "Sprint data will appear once the backend responds.",
      alertTitle: "Loading",
      alertBody: "Connecting to live sprint data.",
      status: "at_risk" as const,
    },
  };

  const membersMap = useMemo(() => createMembersMap(data.members), [data.members]);

  // Enhance tasks with pre-calculated metadata for performance
  const enhancedTasks = useMemo(() => {
    return data.tasks.map((task) => ({
      ...task,
      dueState: getDueDateState(task.dueDate),
    }));
  }, [data.tasks]);

  const filteredTasks = useMemo(
    () => filterTasks(enhancedTasks, filters, membersMap),
    [enhancedTasks, filters, membersMap],
  );

  const tasksByStatus = useMemo(() => groupTasksByStatus(filteredTasks), [filteredTasks]);
  const progress = useMemo(() => getSprintProgress(enhancedTasks), [enhancedTasks]);
  const pointSummary = useMemo(() => getSprintPointSummary(enhancedTasks), [enhancedTasks]);

  const stats = useMemo(
    () => [
      { id: "total", label: "Total Points", value: String(pointSummary.total) },
      {
        id: "completed",
        label: "Completed",
        value: String(pointSummary.completed),
        tone: "success" as const,
      },
      {
        id: "remaining",
        label: "Remaining",
        value: String(pointSummary.remaining),
        tone: "warning" as const,
      },
    ],
    [pointSummary.completed, pointSummary.remaining, pointSummary.total],
  );

  const onDropTask = useCallback(
    (status: SprintTaskStatus) => {
      if (!draggingTaskId || !boardData) {
        return;
      }

      const sourceTask = boardData.tasks.find((task) => task.id === draggingTaskId);
      if (!sourceTask) {
        return;
      }

      setBoardData((current) =>
        current
          ? {
              ...current,
              tasks: moveTaskToStatus(current.tasks, draggingTaskId, status),
            }
          : current,
      );

      void updateTaskStatus(draggingTaskId, status, projectId, sourceTask.version)
        .then(() => loadBoardData())
        .catch((err) => {
          setError(err instanceof Error ? err.message : "Failed to update task status");
          void loadBoardData();
        });

      setDraggingTaskId(null);
    },
    [boardData, draggingTaskId, loadBoardData, projectId],
  );

  const onCreateTask = useCallback(
    (input: Parameters<typeof createSprintTask>[0]) => {
      void createSprintTask(input, projectId)
        .then(() => loadBoardData())
        .catch((err) => {
          setError(err instanceof Error ? err.message : "Failed to create task");
        });
    },
    [loadBoardData, projectId],
  );

  if (isLoading) {
    return <SprintSkeleton />;
  }

  if (!boardData) {
    return (
      <AppLayout title="Sprint">
        <div className="rounded-[24px] border border-rose-200 bg-white p-6 text-slate-700 shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
          <p className="text-[18px] font-semibold text-slate-800">Gagal memuat sprint</p>
          <p className="mt-2 text-[14px] leading-6 text-slate-500">{error ?? "Unknown error"}</p>
          <button
            type="button"
            onClick={loadBoardData}
            className="mt-5 rounded-2xl bg-[#3f2fd6] px-4 py-3 text-[14px] font-semibold text-white"
          >
            Coba lagi
          </button>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout
      title={data.sprint.name}
      breadcrumbs={[
        { label: "Sprints" },
        { label: data.sprint.name },
      ]}
    >
      <div className="space-y-6">
        <SprintOverview
          sprint={data.sprint}
          progress={progress}
          onOpenCreateTask={() => setShowTaskModal(true)}
          onCreateSprint={() => {
            setIsCreatingSprint(true);
            setTimeout(() => setIsCreatingSprint(false), 700);
          }}
        />

        <div className="grid gap-4 rounded-[24px] border border-slate-200 bg-white p-5 shadow-[0_12px_28px_rgba(15,23,42,0.05)] sm:grid-cols-2 lg:grid-cols-3">
          <label className="space-y-1.5">
            <span className="text-[11px] font-bold tracking-wider text-slate-500 uppercase px-1">
              Filter by priority
            </span>
            <select
              value={filters.priority}
              onChange={(event) =>
                setFilters((current) => ({
                  ...current,
                  priority: event.target.value as SprintFilterState["priority"],
                }))
              }
              className="h-11 w-full rounded-2xl border border-slate-200 bg-slate-50/50 px-4 text-sm font-medium text-slate-700 focus:bg-white focus:ring-2 focus:ring-[#4338ca] transition-all"
            >
              <option value="all">All priorities</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </label>

          <label className="space-y-1.5">
            <span className="text-[11px] font-bold tracking-wider text-slate-500 uppercase px-1">
              Filter by assignee
            </span>
            <select
              value={filters.assigneeId}
              onChange={(event) =>
                setFilters((current) => ({
                  ...current,
                  assigneeId: event.target.value,
                }))
              }
              className="h-11 w-full rounded-2xl border border-slate-200 bg-slate-50/50 px-4 text-sm font-medium text-slate-700 focus:bg-white focus:ring-2 focus:ring-[#4338ca] transition-all"
            >
              <option value="all">All members</option>
              {boardData.members.map((member) => (
                <option key={member.id} value={member.id}>
                  {member.name}
                </option>
              ))}
            </select>
          </label>

          <div className="flex items-end">
            <button
              type="button"
              onClick={() => setFilters(defaultFilters)}
              className="h-11 w-full sm:w-auto rounded-2xl border border-slate-200 px-6 text-sm font-bold text-slate-600 hover:bg-slate-50 hover:text-slate-900 transition-all shadow-sm"
            >
              Reset Filters
            </button>
          </div>
        </div>

        <div className="grid gap-6 2xl:grid-cols-[minmax(0,1fr)_340px]">
          <section className="space-y-6">
            <SprintStatCards stats={stats.length ? stats : data.stats} />
            {filteredTasks.length ? (
              <div className="bg-white rounded-[28px] border border-slate-200 p-2 shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
                <KanbanBoard
                  tasksByStatus={tasksByStatus}
                  membersMap={membersMap}
                  onDropTask={onDropTask}
                  onDragStart={setDraggingTaskId}
                  onDragEnd={() => setDraggingTaskId(null)}
                />
              </div>
            ) : (
              <SprintEmptyState
                title="No tasks found"
                description="No sprint tasks match the current search and filter combination."
              />
            )}
          </section>

          <aside className="space-y-6">
            <section className="rounded-[28px] border border-[#e0daf5] bg-[linear-gradient(180deg,#fbf9ff_0%,#f7f4ff_100%)] shadow-[0_12px_28px_rgba(15,23,42,0.05)] overflow-hidden">
              <div className="border-b border-[#e5def7] px-6 py-5">
                <div className="flex items-center gap-2">
                  <span className="text-xl">✨</span>
                  <h3 className="text-[20px] font-bold tracking-tight text-slate-800">{data.insights.title}</h3>
                </div>
                <p className="text-[13px] font-medium text-slate-500 mt-1">{data.insights.subtitle}</p>
              </div>
              <div className="space-y-5 px-6 py-5 text-[15px] leading-relaxed text-slate-600 font-medium">
                <p>
                  The team is currently{" "}
                  <span
                    className={`font-bold px-2 py-0.5 rounded-lg border ${
                      data.insights.status === "on_track"
                        ? "text-emerald-600 bg-emerald-50 border-emerald-100"
                        : "text-amber-600 bg-amber-50 border-amber-100"
                    }`}
                  >
                    {data.insights.status === "on_track" ? "on track" : "at risk"}
                  </span>{" "}
                  to meet sprint goals.
                </p>
                <div className="rounded-[20px] bg-white border border-[#e5def7] p-4 shadow-sm">
                  <p className="font-bold text-amber-600 flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-amber-500 animate-pulse" />
                    {data.insights.alertTitle}
                  </p>
                  <p className="text-[13px] text-slate-500 mt-1.5 font-medium">
                    {data.insights.alertBody}
                  </p>
                </div>
                <button className="w-full rounded-2xl bg-[#4338ca] px-4 py-3 text-[14px] font-bold text-white shadow-[0_10px_24px_rgba(67,56,202,0.2)] hover:bg-[#3f2fd6] transition-all">
                  View Full Activity Log
                </button>
              </div>
            </section>

            <section className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
              <h3 className="text-[22px] font-bold tracking-tight text-slate-800">Sprint Velocity</h3>
              <div className="mt-5 grid grid-cols-4 text-center text-[12px] font-bold text-slate-400 uppercase tracking-widest px-1">
                {data.velocity.map((point, index) => (
                  <span key={point.label} className={index === data.velocity.length - 1 ? "text-[#4338ca]" : ""}>
                    {point.label}
                  </span>
                ))}
              </div>
              <div className="mt-6 border-t border-slate-100 pt-5 flex items-center justify-between">
                <span className="text-sm font-bold text-slate-500">Rolling Average</span>
                <span className="text-[26px] font-bold text-slate-800 tracking-tight">
                  {Math.round(data.velocity.reduce((sum, point) => sum + point.value, 0) / Math.max(data.velocity.length, 1)) || 0} pts
                </span>
              </div>
            </section>

            <section className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
              <h3 className="text-[22px] font-bold tracking-tight text-slate-800">Active Team</h3>
              <div className="mt-5 flex -space-x-3 px-1">
                {data.members.map((member) => (
                  <span
                    key={member.id}
                    title={member.name}
                    className="inline-flex h-11 w-11 items-center justify-center rounded-full border-4 border-white text-[12px] font-bold text-white shadow-sm hover:-translate-y-1 transition-transform"
                    style={{ backgroundColor: member.color }}
                  >
                    {member.avatar}
                  </span>
                ))}
              </div>
            </section>
          </aside>
        </div>
      </div>

      <CreateTaskModal
        open={showTaskModal}
        members={data.members}
        onClose={() => setShowTaskModal(false)}
        onCreate={onCreateTask}
      />

      {isCreatingSprint ? (
        <div className="fixed right-4 bottom-4 rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white shadow-[0_10px_28px_rgba(15,23,42,0.32)]">
          Creating sprint...
        </div>
      ) : null}
    </AppLayout>
  );
}
