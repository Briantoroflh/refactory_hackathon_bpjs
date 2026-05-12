export interface EngineerPerformance {
  id: string;
  name: string;
  role: string;
  velocity: number;
  quality: number;
  score: number;
  status: "optimal" | "warning" | "critical";
  avatar?: string;
}

export interface AIInsight {
  id: string;
  title: string;
  description: string;
  severity: "info" | "warning" | "critical";
  metric?: string;
  trend?: "up" | "down" | "stable";
}

export interface TeamAnalytics {
  sprintId: string;
  sprintNumber: number;
  quarter: string;
  year: number;
  teamVelocity: {
    current: number;
    previous: number;
    trend: number;
    completedPoints: number;
  };
  engineers: EngineerPerformance[];
  insights: AIInsight[];
  dateRange: {
    start: string;
    end: string;
  };
}
