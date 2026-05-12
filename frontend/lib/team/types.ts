export interface TeamMember {
  id: string;
  name: string;
  email: string;
  role: "Admin" | "Developer" | "Viewer" | string;
  status: "Active" | "Pending" | "Inactive" | string;
  avatar?: string;
  joinDate?: string;
}

export interface ModulePermission {
  id: string;
  name: string;
  read: boolean;
  write: boolean;
  delete: boolean;
}

export interface TeamAccessControl {
  team?: {
    team_id: number;
    name: string;
    description?: string | null;
    category_id: number;
    status: string;
    capacity_hours: number;
    member_count: number;
  } | null;
  teams?: {
    team_id: number;
    name: string;
    description?: string | null;
    category_id: number;
    status: string;
    capacity_hours: number;
    member_count: number;
  }[];
  members: TeamMember[];
  totalMembers: number;
  permissions: ModulePermission[];
  notice?: string | null;
}
