"use client";

import dynamic from "next/dynamic";
import { useCallback, useEffect, useMemo, useState } from "react";
import { createTaskFromInput, moveTaskToStatus } from "@/lib/sprints/board";
import { fetchSprintBoardData } from "@/lib/sprints/api";
import { sprintBoardMockData } from "@/lib/sprints/mock-data";
import {
  createMembersMap,
  filterTasks,
  getDueDateState,
  getSprintPointSummary,
  getSprintProgress,
  groupTasksByStatus,
} from "@/lib/sprints/selectors";
import type { SprintBoardData, SprintFilterState, SprintTaskStatus } from "@/lib/sprints/types";
import { SprintNavbar } from "./sprint-navbar";
import { SprintSidebar } from "./sprint-sidebar";
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
  const [boardData, setBoardData] = useState<SprintBoardData>(sprintBoardMockData);
  const [filters, setFilters] = useState<SprintFilterState>(defaultFilters);
  const [draggingTaskId, setDraggingTaskId] = useState<string | null>(null);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreatingSprint, setIsCreatingSprint] = useState(false);

  useEffect(() => {
    let isMounted = true;

    async function syncBoardData() {
      setIsLoading(true);

      try {
        const data = await fetchSprintBoardData();
        if (isMounted) {
          setBoardData(data);
        }
      } catch {
        if (isMounted) {
          setBoardData(sprintBoardMockData);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    void syncBoardData();

    return () => {
      isMounted = false;
    };
  }, []);

  const membersMap = useMemo(() => createMembersMap(boardData.members), [boardData.members]);

  // Enhance tasks with pre-calculated metadata for performance
  const enhancedTasks = useMemo(() => {
    return boardData.tasks.map(task => ({
      ...task,
      dueState: getDueDateState(task.dueDate)
    }));
  }, [boardData.tasks]);

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
      if (!draggingTaskId) {
        return;
      }

      setBoardData((current) => ({
        ...current,
        tasks: moveTaskToStatus(current.tasks, draggingTaskId, status),
      }));
      setDraggingTaskId(null);
    },
    [draggingTaskId],
  );

  const onCreateTask = useCallback((input: Parameters<typeof createTaskFromInput>[0]) => {
    setBoardData((current) => ({
      ...current,
      tasks: [...current.tasks, createTaskFromInput(input)],
    }));
  }, []);

  if (isLoading) {
    return <SprintSkeleton />;
  }

  return (
    <div className="min-h-screen bg-[#eef1f8] p-3 text-slate-900 sm:p-4">
      <div className="mx-auto flex min-h-[calc(100vh-1.5rem)] w-full overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-[0_12px_38px_rgba(15,23,42,0.12)]">
        <SprintSidebar
          open={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          items={boardData.sidebarItems}
        />

        <div className="flex min-w-0 flex-1 flex-col">
          <SprintNavbar
            query={filters.query}
            breadcrumbs={boardData.sprint.projectPath}
            onOpenSidebar={() => setSidebarOpen(true)}
            onQueryChange={(query) => setFilters((current) => ({ ...current, query }))}
          />

          <main className="flex-1 overflow-y-auto bg-[#f8f9fd] px-4 py-5 sm:px-6 lg:px-8">
            <SprintOverview
              sprint={boardData.sprint}
              progress={progress}
              onOpenCreateTask={() => setShowTaskModal(true)}
              onCreateSprint={() => {
                setIsCreatingSprint(true);
                setTimeout(() => setIsCreatingSprint(false), 700);
              }}
            />

            <div className="mt-5 grid gap-3 rounded-2xl border border-[#dbe0ef] bg-white p-4 sm:grid-cols-2 lg:grid-cols-3">
              <label className="space-y-1">
                <span className="text-xs font-semibold tracking-wide text-slate-500 uppercase">
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
                  className="h-10 w-full rounded-xl border border-slate-200 bg-white px-3 text-sm text-slate-700"
                >
                  <option value="all">All priorities</option>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </label>

              <label className="space-y-1">
                <span className="text-xs font-semibold tracking-wide text-slate-500 uppercase">
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
                  className="h-10 w-full rounded-xl border border-slate-200 bg-white px-3 text-sm text-slate-700"
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
                  className="h-10 rounded-xl border border-slate-200 px-4 text-sm font-semibold text-slate-600 hover:bg-slate-50"
                >
                  Reset Filters
                </button>
              </div>
            </div>

            <div className="mt-6 grid gap-5 2xl:grid-cols-[minmax(0,1fr)_340px]">
              <section className="space-y-5">
                <SprintStatCards stats={stats.length ? stats : boardData.stats} />
                {filteredTasks.length ? (
                  <KanbanBoard
                    tasksByStatus={tasksByStatus}
                    membersMap={membersMap}
                    onDropTask={onDropTask}
                    onDragStart={setDraggingTaskId}
                    onDragEnd={() => setDraggingTaskId(null)}
                  />
                ) : (
                  <SprintEmptyState
                    title="No tasks found"
                    description="No sprint tasks match the current search and filter combination."
                  />
                )}
              </section>

              <aside className="space-y-5">
                <section className="rounded-3xl border border-[#ccd3ea] bg-white shadow-[0_8px_18px_rgba(15,23,42,0.06)]">
                  <div className="border-b border-slate-200 px-5 py-4">
                    <h3 className="text-[20px] font-semibold tracking-[-0.02em] text-slate-800">
                      AI Standup Insight
                    </h3>
                    <p className="text-[15px] text-slate-500">Synthesized 2 hours ago</p>
                  </div>
                  <div className="space-y-4 px-5 py-4 text-[16px] text-slate-600">
                    <p>
                      The team is currently <span className="font-semibold text-emerald-500">on track</span>{" "}
                      to meet sprint goals. A review bottleneck is detected in migration tasks.
                    </p>
                    <div className="rounded-xl bg-[#f8f9ff] p-3">
                      <p className="font-semibold text-amber-600">Review Delay Detected</p>
                      <p className="text-sm text-slate-500">
                        ENG-390 has been in review for 48 hours. Suggested pairing to expedite.
                      </p>
                    </div>
                    <button className="w-full rounded-xl bg-[#e9e8f4] px-4 py-2.5 text-[15px] font-semibold text-slate-700">
                      View Full Activity Log
                    </button>
                  </div>
                </section>

                <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-[0_8px_18px_rgba(15,23,42,0.06)]">
                  <h3 className="text-[30px] font-semibold tracking-[-0.02em] text-slate-800">Sprint Velocity</h3>
                  <div className="mt-5 grid grid-cols-4 text-center text-sm font-semibold text-slate-500">
                    <span>S39</span>
                    <span>S40</span>
                    <span>S41</span>
                    <span className="text-[#4338ca]">S42</span>
                  </div>
                  <div className="mt-5 border-t border-slate-200 pt-4 text-sm font-semibold text-slate-500">
                    Rolling Average
                    <span className="float-right text-[23px] text-slate-800">82 pts</span>
                  </div>
                </section>

                <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-[0_8px_18px_rgba(15,23,42,0.06)]">
                  <h3 className="text-[30px] font-semibold tracking-[-0.02em] text-slate-800">Active Team</h3>
                  <div className="mt-5 flex -space-x-3">
                    {boardData.members.map((member) => (
                      <span
                        key={member.id}
                        title={member.name}
                        className="inline-flex h-10 w-10 items-center justify-center rounded-full border-2 border-white text-xs font-bold text-white"
                        style={{ backgroundColor: member.color }}
                      >
                        {member.avatar}
                      </span>
                    ))}
                  </div>
                </section>
              </aside>
            </div>
          </main>
        </div>
      </div>

      <CreateTaskModal
        open={showTaskModal}
        members={boardData.members}
        onClose={() => setShowTaskModal(false)}
        onCreate={onCreateTask}
      />

      {isCreatingSprint ? (
        <div className="fixed right-4 bottom-4 rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white shadow-[0_10px_28px_rgba(15,23,42,0.32)]">
          Creating sprint...
        </div>
      ) : null}
    </div>
  );
}
