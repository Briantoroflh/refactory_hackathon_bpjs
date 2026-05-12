import { apiClient } from "@/lib/api/client";
import { fetchProjectsPageData } from "@/lib/projects/api";
import type { TeamAnalytics } from "@/lib/analytics/types";
import type { SprintBoardData } from "@/lib/sprints/types";
import type { AIDocument, AIContextItem, AIMessage, AILiveSnapshot, CodeSnippet } from "./types";

type AIWorkflowKey =
  | "planning"
  | "sprint-summary"
  | "standup-recap"
  | "task-recommendation"
  | "workload-suggestion"
  | "ticket-explanation"
  | "documentation-helper"
  | "bug-analysis"
  | "kanban-jobdesk";

type AIWorkflowResult = {
  workflow: string;
  status: string;
  model: string;
  content: string;
  structured_output?: Record<string, unknown> | null;
  source?: string;
};

function createEmptySnapshot(): AILiveSnapshot {
  return {
    documents: [],
    contextItems: [],
    messages: [
      {
        id: "ai-empty",
        type: "ai",
        content:
          "Saya belum menemukan konteks live yang bisa dimuat. Hubungkan project aktif agar saya bisa membaca sprint, task, dan analytics secara realtime.",
      },
    ],
    requestContext: {},
    notice: "No live project context available yet.",
  };
}

function buildAvatar(name?: string, email?: string): string {
  if (name) {
    return name
      .split(/\s+/)
      .slice(0, 2)
      .map((part) => part[0])
      .join("")
      .toUpperCase();
  }

  return (email ?? "??").slice(0, 2).toUpperCase();
}

function normalizeTitle(value?: string): string {
  return value?.trim() || "Untitled";
}

function selectWorkflow(prompt: string): AIWorkflowKey {
  const text = prompt.toLowerCase();
  if (/bug|error|crash|exception|auth|token|login|failed|issue/.test(text)) {
    return "bug-analysis";
  }
  if (/plan|planning|roadmap|strategy|milestone/.test(text)) {
    return "planning";
  }
  if (/summary|summarize|recap|standup|retrospective/.test(text)) {
    return "sprint-summary";
  }
  if (/task|ticket|assign|kanban|recommend|priority/.test(text)) {
    return "task-recommendation";
  }
  if (/workload|capacity|balance|allocation/.test(text)) {
    return "workload-suggestion";
  }
  if (/explain|ticket|why|how does|how to/.test(text)) {
    return "ticket-explanation";
  }
  if (/doc|documentation|spec|api|guide/.test(text)) {
    return "documentation-helper";
  }
  return "documentation-helper";
}

export async function fetchAILiveSnapshot(): Promise<AILiveSnapshot> {
  const projectsData = await fetchProjectsPageData();
  const project = projectsData.projects[0];

  if (!project) {
    return createEmptySnapshot();
  }

  const projectId = Number(project.id);
  if (!Number.isFinite(projectId)) {
    return createEmptySnapshot();
  }

  const [sprintResult, analyticsResult, tasksResult] = await Promise.allSettled([
    apiClient.get<SprintBoardData>(`/projects/${projectId}/sprint-overview`),
    apiClient.get<TeamAnalytics>(`/projects/${projectId}/analytics-overview`),
    apiClient.get<Array<Record<string, unknown>>>(`/projects/${projectId}/tasks?skip=0&limit=20`),
  ]);

  const sprint = sprintResult.status === "fulfilled" ? sprintResult.value : null;
  const analytics = analyticsResult.status === "fulfilled" ? analyticsResult.value : null;
  const tasks = tasksResult.status === "fulfilled" ? tasksResult.value : [];

  const primaryInsight = analytics?.insights?.[0];
  const activeTask = tasks.find((task) => String(task.status ?? "").toLowerCase() !== "completed");
  const topTask = tasks[0];
  const assistantIntro = `Saya memuat konteks live untuk ${project.name}${sprint ? ` / ${sprint.sprint.name}` : ""}. `;
  const assistantSummary = analytics
    ? `Velocity saat ini ${analytics.teamVelocity.current} poin, insight utama "${primaryInsight?.title ?? "tidak ada"}".`
    : "Analytics belum tersedia sepenuhnya, tapi project dan sprint aktif sudah terhubung.";

  const documents: AIDocument[] = [
    {
      id: "project-doc",
      title: normalizeTitle(project.name),
      updated: `Health ${project.aiHealthScore ?? 0}/100 • ${String(project.status ?? "unknown")}`,
      type: "documentation",
    },
    {
      id: "sprint-doc",
      title: sprint ? normalizeTitle(sprint.sprint.name) : "Active Sprint",
      updated: sprint
        ? `${sprint.sprint.startDateLabel} - ${sprint.sprint.endDateLabel}`
        : "Sprint data unavailable",
      type: "documentation",
    },
  ];

  if (primaryInsight) {
    documents.push({
      id: "insight-doc",
      title: primaryInsight.title,
      status: primaryInsight.description,
      type: "issue",
    });
  }

  if (topTask) {
    documents.push({
      id: "task-doc",
      title: String(topTask.title ?? "Untitled task"),
      status: `Task status: ${String(topTask.status ?? "backlog")}`,
      type: "issue",
    });
  }

  const contextItems: AIContextItem[] = [
    {
      id: "ctx-sprint",
      type: "active",
      label: sprint ? `${sprint.sprint.name} • ${sprint.sprint.daysRemaining} days left` : `${project.name} • active project`,
    },
  ];

  if (activeTask) {
    contextItems.push({
      id: "ctx-task",
      type: "recent",
      label: String(activeTask.title ?? "Active task"),
    });
  }

  if (primaryInsight) {
    contextItems.push({
      id: "ctx-insight",
      type: "recent",
      label: primaryInsight.title,
    });
  }

  const messages: AIMessage[] = [
    {
      id: "ai-live-intro",
      type: "ai",
      content: `${assistantIntro}${assistantSummary} Kirim pertanyaan untuk analisis bug, planning, rekomendasi task, atau dokumentasi.`,
    },
  ];

  if (activeTask) {
    messages.push({
      id: "ai-live-task",
      type: "ai",
      content: `Task live yang paling dekat: ${String(activeTask.title ?? "Untitled task")} dengan status ${String(activeTask.status ?? "backlog")}.`,
    });
  }

  return {
    documents,
    contextItems,
    messages,
    requestContext: {
      projectId,
      projectName: project.name,
      sprintId: sprint?.sprint.id ?? `project-${projectId}-sprint`,
      sprintName: sprint?.sprint.name ?? normalizeTitle(project.name),
      analytics: analytics ?? undefined,
      activeTask: activeTask
        ? {
            id: String(activeTask.task_id ?? activeTask.id ?? ""),
            title: String(activeTask.title ?? ""),
            status: String(activeTask.status ?? ""),
            priority: String(activeTask.priority ?? "medium"),
          }
        : undefined,
      documents,
    },
    notice:
      sprintResult.status === "rejected" || analyticsResult.status === "rejected" || tasksResult.status === "rejected"
        ? "Some live AI context could not be loaded."
        : undefined,
  };
}

export async function sendAIMessage(
  prompt: string,
  context: Record<string, unknown>,
): Promise<{ content: string; codeSnippet?: CodeSnippet }> {
  const workflow = selectWorkflow(prompt);
  const response = await apiClient.post<AIWorkflowResult>(`/ai-assistant/${workflow}`, {
    prompt,
    context,
    async_mode: false,
  });

  return {
    content: response.content || "Saya belum mendapatkan output yang bisa ditampilkan.",
    codeSnippet:
      response.structured_output && Object.keys(response.structured_output).length
        ? {
            code: JSON.stringify(response.structured_output, null, 2),
            language: "json",
          }
        : undefined,
  };
}
