export type SprintTaskStatus = "todo" | "in_progress" | "review" | "done";

export type SprintTaskPriority = "low" | "medium" | "high" | "critical";

export type SprintMember = {
  id: string;
  name: string;
  avatar: string;
  color: string;
};

export type SprintTask = {
  id: string;
  title: string;
  status: SprintTaskStatus;
  priority: SprintTaskPriority;
  dueDate: string;
  storyPoints: number;
  tags: string[];
  assigneeIds: string[];
  version?: number;
  dueState?: {
    label: string;
    tone: "neutral" | "warning" | "danger";
  };
};

export type SprintSummary = {
  id: string;
  name: string;
  projectPath: string[];
  startDateLabel: string;
  endDateLabel: string;
  daysRemaining: number;
  storyPointGoal: number;
};

export type SprintStat = {
  id: string;
  label: string;
  value: string;
  tone?: "default" | "success" | "warning";
};

export type SprintSidebarItem = {
  label: string;
  href: string;
  icon:
    | "dashboard"
    | "project"
    | "sprint"
    | "tasks"
    | "analytics"
    | "ai"
    | "team"
    | "settings";
  active?: boolean;
};

export type SprintBoardData = {
  sprint: SprintSummary;
  members: SprintMember[];
  stats: SprintStat[];
  tasks: SprintTask[];
  sidebarItems: SprintSidebarItem[];
  velocity: Array<{ label: string; value: number }>;
  insights: {
    title: string;
    subtitle: string;
    summary: string;
    alertTitle: string;
    alertBody: string;
    status: "on_track" | "at_risk";
  };
  generatedAt?: string;
};

export type SprintFilterState = {
  query: string;
  priority: "all" | SprintTaskPriority;
  assigneeId: "all" | string;
};

export type CreateTaskInput = {
  title: string;
  priority: SprintTaskPriority;
  status: SprintTaskStatus;
  dueDate: string;
  storyPoints: number;
  tags: string[];
  assigneeIds: string[];
};
