import type { TeamAccessControl } from "./types";

export const mockTeamAccessControl: TeamAccessControl = {
  members: [
    {
      id: "member-1",
      name: "Elena Silva",
      email: "elena.silva@sprintflow.com",
      role: "Admin",
      status: "Active",
      avatar: "ES",
      joinDate: "2023-01-15",
    },
    {
      id: "member-2",
      name: "Marcus Kline",
      email: "marcus.k@sprintflow.com",
      role: "Developer",
      status: "Active",
      avatar: "MK",
      joinDate: "2023-03-20",
    },
    {
      id: "member-3",
      name: "Jessica Lin",
      email: "jlin@sprintflow.com",
      role: "Viewer",
      status: "Pending",
      avatar: "JL",
      joinDate: "2023-05-10",
    },
  ],
  totalMembers: 24,
  permissions: [
    {
      id: "perm-1",
      name: "Projects",
      read: true,
      write: true,
      delete: true,
    },
    {
      id: "perm-2",
      name: "Sprints",
      read: true,
      write: true,
      delete: true,
    },
    {
      id: "perm-3",
      name: "Analytics",
      read: false,
      write: false,
      delete: false,
    },
  ],
};
