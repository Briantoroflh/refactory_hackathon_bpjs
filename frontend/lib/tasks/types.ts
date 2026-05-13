export interface TaskCard {
  id: string;
  title: string;
  description: string;
  label: string;
  priority: "low" | "medium" | "high";
  status?: "todo" | "in_progress" | "review" | "done";
  version?: number;
  assignee?: {
    name: string;
    avatar: string;
  };
  progress?: number;
  dueDate?: string;
}

export interface TaskColumn {
  id: string;
  title: string;
  count: number;
  cards: TaskCard[];
}

export interface SprintTasks {
  sprintNumber?: number;
  sprintTitle: string;
  dateRange: string;
  repositoryLink: string;
  repositoryHref?: string;
  columns: TaskColumn[];
  generatedAt?: string;
}
