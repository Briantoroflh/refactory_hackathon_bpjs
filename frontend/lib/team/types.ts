export interface TeamMember {
  id: string;
  name: string;
  email: string;
  role: "Admin" | "Developer" | "Viewer";
  status: "Active" | "Pending" | "Inactive";
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
  members: TeamMember[];
  totalMembers: number;
  permissions: ModulePermission[];
}
