import type { SprintTasks } from "./types";

export const mockSprintTasks: SprintTasks = {
  sprintNumber: 42,
  sprintTitle: "Authentication Refactor",
  dateRange: "Oct 12 - Oct 26",
  repositoryLink: "sprintflow/auth-service",
  columns: [
    {
      id: "todo",
      title: "To Do",
      count: 3,
      cards: [
        {
          id: "task-1",
          title: "Implement JWT refresh token rotation mechanism",
          description:
            "Add automatic token refresh with proper expiry handling",
          label: "AUTH-101",
          priority: "high",
          assignee: {
            name: "Sarah J.",
            avatar: "SJ",
          },
        },
        {
          id: "task-2",
          title: "Set up OAuth 2.0 integration",
          description: "",
          label: "AUTH-102",
          priority: "medium",
          assignee: {
            name: "Mike T.",
            avatar: "MT",
          },
        },
        {
          id: "task-3",
          title: "Add multi-factor authentication",
          description: "",
          label: "AUTH-103",
          priority: "high",
          assignee: {
            name: "Alex M.",
            avatar: "AM",
          },
        },
      ],
    },
    {
      id: "inprogress",
      title: "In Progress",
      count: 2,
      cards: [
        {
          id: "task-4",
          title: "Migrate user sessions to Redis cluster",
          description:
            "Move session store from memory to Redis for scalability",
          label: "AUTH-201",
          priority: "high",
          progress: 60,
          assignee: {
            name: "Sarah J.",
            avatar: "SJ",
          },
        },
        {
          id: "task-5",
          title: "Implement password reset flow",
          description: "",
          label: "AUTH-202",
          priority: "medium",
          assignee: {
            name: "Jamie R.",
            avatar: "JR",
          },
        },
      ],
    },
    {
      id: "review",
      title: "Review",
      count: 1,
      cards: [
        {
          id: "task-6",
          title: "Fix OAuth callback URL parsing error on mobile Safari",
          description: "Resolve issue with mobile browser OAuth redirect",
          label: "AUTH-203",
          priority: "high",
          assignee: {
            name: "Casey L.",
            avatar: "CL",
          },
        },
      ],
    },
  ],
};
