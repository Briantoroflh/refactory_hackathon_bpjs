export type DashboardNavItem = {
  label: string;
  href: string;
  icon: string;
  active?: boolean;
};

export type StatCard = {
  title: string;
  value: string;
  delta: string;
  deltaDirection: "up" | "down";
  description: string;
  accent: string;
  icon: string;
};

export type SprintBar = {
  label: string;
  value: number;
  active?: boolean;
};

export type ActivityItem = {
  id: string;
  title: string;
  project: string;
  owner: string;
  timestamp: string;
  status: "done" | "in progress" | "review";
};

export type NotificationItem = {
  id: string;
  title: string;
  description: string;
  tone: "info" | "warning" | "success";
};

export type DashboardProfile = {
  name: string;
  title: string;
  projects: number;
  team: number;
};

export type DashboardOverview = {
  generatedAt: string;
  profile: DashboardProfile;
  stats: StatCard[];
  sprint: {
    title: string;
    subtitle: string;
    bars: SprintBar[];
  };
  activities: ActivityItem[];
  notifications: NotificationItem[];
};
