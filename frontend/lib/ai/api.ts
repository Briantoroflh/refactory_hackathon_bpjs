import { ApiClientError, apiClient } from "@/lib/api/client";
import { fetchProjectsPageData } from "@/lib/projects/api";
import type { TeamAnalytics } from "@/lib/analytics/types";
import type { SprintBoardData } from "@/lib/sprints/types";
import type { AIDocument, AIContextItem, AIMessage, AILiveSnapshot, CodeSnippet } from "./types";

const AI_REQUEST_TIMEOUT_MS = 20000;
const AI_MAX_RETRIES = 1;
export const AI_MAX_PROMPT_LENGTH = 2000;

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

export class AIAssistantError extends Error {
  status: number | null;
  retryable: boolean;
  code: string;

  constructor(message: string, status: number | null, retryable: boolean, code: string) {
    super(message);
    this.name = "AIAssistantError";
    this.status = status;
    this.retryable = retryable;
    this.code = code;
  }
}

type AIErrorShape = {
  message: string;
  status: number | null;
  retryable: boolean;
  code: string;
};

function maskPrompt(prompt: string): string {
  const compact = prompt.replace(/\s+/g, " ").trim();
  if (!compact) {
    return "[empty]";
  }
  const preview = compact.slice(0, 24);
  return `${preview}${compact.length > 24 ? "..." : ""} (len:${compact.length})`;
}

function emitAIEvent(event: string, meta: Record<string, unknown>): void {
  // Keep telemetry lightweight and sanitized (no raw prompt content).
  if (typeof window !== "undefined") {
    console.info("[ai-telemetry]", event, meta);
  }
}

export function validateAIPrompt(input: string): { ok: true; prompt: string } | { ok: false; message: string } {
  const prompt = input.trim();
  if (!prompt) {
    return { ok: false, message: "Prompt tidak boleh kosong." };
  }
  if (prompt.length > AI_MAX_PROMPT_LENGTH) {
    return {
      ok: false,
      message: `Prompt terlalu panjang. Maksimal ${AI_MAX_PROMPT_LENGTH} karakter.`,
    };
  }
  return { ok: true, prompt };
}

export function normalizeAIResponse(response: Partial<AIWorkflowResult> | null | undefined): AIWorkflowResult {
  return {
    workflow: response?.workflow || "unknown",
    status: response?.status || "completed",
    model: response?.model || "unknown",
    content: response?.content || "Saya belum mendapatkan output yang bisa ditampilkan.",
    structured_output: response?.structured_output ?? null,
    source: response?.source || "openrouter",
  };
}

export function getAIActionHint(status: number | null): string {
  if (status === 401) {
    return "Silakan login ulang untuk melanjutkan.";
  }
  if (status === 422) {
    return "Periksa prompt lalu kirim ulang.";
  }
  if (status === 408 || status === 429 || (status !== null && status >= 500)) {
    return "Layanan AI sedang sibuk, coba lagi dalam beberapa detik.";
  }
  return "Silakan coba lagi.";
}

function isTransientStatus(status: number | null): boolean {
  return status === 408 || status === 429 || (status !== null && status >= 500);
}

export function mapAIError(error: unknown): AIErrorShape {
  if (error instanceof AIAssistantError) {
    return {
      message: error.message,
      status: error.status,
      retryable: error.retryable,
      code: error.code,
    };
  }

  if (error instanceof ApiClientError) {
    const status = error.status ?? null;
    if (status === 401) {
      return {
        message: "Sesi login Anda berakhir. Silakan login ulang lalu coba lagi.",
        status,
        retryable: false,
        code: "AUTH_REQUIRED",
      };
    }
    if (status === 422) {
      return {
        message: "Permintaan AI tidak valid. Periksa input lalu coba lagi.",
        status,
        retryable: false,
        code: "VALIDATION_FAILED",
      };
    }
    if (isTransientStatus(status)) {
      return {
        message: "Layanan AI sedang sibuk. Silakan coba beberapa saat lagi.",
        status,
        retryable: true,
        code: "TRANSIENT_FAILURE",
      };
    }
    return {
      message: error.message || "Terjadi gangguan saat memproses AI assistant.",
      status,
      retryable: false,
      code: "UNKNOWN_API_ERROR",
    };
  }

  if (error instanceof Error && error.name === "AbortError") {
    return {
      message: "Permintaan AI timeout. Silakan coba lagi.",
      status: 408,
      retryable: true,
      code: "REQUEST_TIMEOUT",
    };
  }

  if (error instanceof Error) {
    return {
      message: error.message || "Terjadi kesalahan tak terduga pada AI assistant.",
      status: null,
      retryable: true,
      code: "NETWORK_OR_UNKNOWN",
    };
  }

  return {
    message: "Terjadi kesalahan tak terduga pada AI assistant.",
    status: null,
    retryable: true,
    code: "UNKNOWN",
  };
}

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
  const validation = validateAIPrompt(prompt);
  if (!validation.ok) {
    throw new AIAssistantError(validation.message, 422, false, "CLIENT_VALIDATION");
  }

  const cleanPrompt = validation.prompt;
  const workflow = selectWorkflow(cleanPrompt);
  emitAIEvent("request.submit", {
    workflow,
    prompt: maskPrompt(cleanPrompt),
    hasContext: Object.keys(context ?? {}).length > 0,
  });

  for (let attempt = 0; attempt <= AI_MAX_RETRIES; attempt += 1) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), AI_REQUEST_TIMEOUT_MS);

    try {
      const raw = await apiClient.post<AIWorkflowResult>(
        `/ai-assistant/${workflow}`,
        {
          prompt: cleanPrompt,
          context: context ?? {},
          async_mode: false,
        },
        { signal: controller.signal },
      );

      const response = normalizeAIResponse(raw);
      emitAIEvent("request.success", {
        workflow,
        attempt: attempt + 1,
        status: response.status,
      });

      return {
        content: response.content,
        codeSnippet:
          response.structured_output && Object.keys(response.structured_output).length
            ? {
                code: JSON.stringify(response.structured_output, null, 2),
                language: "json",
              }
            : undefined,
      };
    } catch (error) {
      const mapped = mapAIError(error);
      const shouldRetry = mapped.retryable && attempt < AI_MAX_RETRIES;

      if (shouldRetry) {
        emitAIEvent("request.retry", {
          workflow,
          attempt: attempt + 1,
          status: mapped.status,
          code: mapped.code,
        });
        continue;
      }

      emitAIEvent("request.fail", {
        workflow,
        attempt: attempt + 1,
        status: mapped.status,
        code: mapped.code,
      });

      throw new AIAssistantError(
        mapped.message,
        mapped.status,
        mapped.retryable,
        mapped.code,
      );
    } finally {
      clearTimeout(timeout);
    }
  }

  throw new AIAssistantError(
    "Layanan AI sedang sibuk. Silakan coba beberapa saat lagi.",
    503,
    true,
    "RETRY_EXHAUSTED",
  );
}
