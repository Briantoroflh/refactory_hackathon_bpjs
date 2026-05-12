export type PlatformType = "GitHub" | "GitLab" | "GitHub Enterprise" | "GitLab Cloud";

export type ProjectStatus = "healthy" | "warning" | "critical";

export type ProjectMember = {
  id: string;
  name: string;
  avatar: string;
};

export type ProjectItem = {
  id: string;
  name: string;
  platform: PlatformType;
  description: string;
  status: ProjectStatus;
  aiHealthScore: number;
  healthDelta: number;
  commitVelocity: number;
  commitBars: number[];
  progress: number;
  updatedAtLabel: string;
  members: ProjectMember[];
};

export type ConnectionStatus = "syncing" | "paused" | "failed";

export type RepositoryConnection = {
  id: string;
  repositoryName: string;
  platform: PlatformType;
  status: ConnectionStatus;
};

export type ProjectListView = "grid" | "list";

export type ProjectSortOption = "updated" | "health-desc" | "health-asc" | "velocity-desc";

export type ProjectFilterState = {
  query: string;
  platform: "all" | PlatformType;
  status: "all" | ProjectStatus;
  sortBy: ProjectSortOption;
  view: ProjectListView;
};

export type ProjectsPageData = {
  projects: ProjectItem[];
  repositories: RepositoryConnection[];
};

