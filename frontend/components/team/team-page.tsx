"use client";

import { useState } from "react";
import { TeamNavbar } from "./team-navbar";
import { TeamSidebar } from "./team-sidebar";
import type {
  TeamAccessControl,
  TeamMember,
  ModulePermission,
} from "@/lib/team/types";

type TeamPageProps = {
  accessControl: TeamAccessControl;
};

function StatusBadge({ status }: { status: string }) {
  const variants = {
    Active: "bg-emerald-50 text-emerald-700 border-emerald-200",
    Pending: "bg-amber-50 text-amber-700 border-amber-200",
    Inactive: "bg-slate-50 text-slate-700 border-slate-200",
  };
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-[12px] font-semibold ${
        variants[status as keyof typeof variants]
      }`}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {status}
    </span>
  );
}

function RoleBadge({ role }: { role: string }) {
  const variants = {
    Admin: "bg-blue-50 text-blue-700 border-blue-200",
    Developer: "bg-purple-50 text-purple-700 border-purple-200",
    Viewer: "bg-slate-50 text-slate-700 border-slate-200",
  };
  return (
    <span
      className={`inline-flex rounded-lg border px-2.5 py-1 text-[12px] font-semibold ${
        variants[role as keyof typeof variants]
      }`}
    >
      {role}
    </span>
  );
}

function PermissionToggle({ enabled }: { enabled: boolean }) {
  return (
    <button
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition ${
        enabled ? "bg-emerald-500" : "bg-slate-300"
      }`}
      aria-pressed={enabled}
    >
      <span
        className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
          enabled ? "translate-x-6" : "translate-x-1"
        }`}
      />
    </button>
  );
}

function ActiveMembersTable({ members }: { members: TeamMember[] }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white overflow-hidden">
      <table className="w-full">
        <thead>
          <tr className="border-b border-slate-200 bg-slate-50">
            <th className="px-6 py-3 text-left text-[12px] font-semibold text-slate-600 uppercase tracking-wider">
              Name
            </th>
            <th className="px-6 py-3 text-left text-[12px] font-semibold text-slate-600 uppercase tracking-wider">
              Role
            </th>
            <th className="px-6 py-3 text-left text-[12px] font-semibold text-slate-600 uppercase tracking-wider">
              Status
            </th>
            <th className="px-6 py-3 text-center text-[12px] font-semibold text-slate-600 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody>
          {members.map((member, index) => (
            <tr
              key={member.id}
              className="border-b border-slate-100 last:border-b-0"
            >
              <td className="px-6 py-4">
                <div className="flex items-center gap-3">
                  <div className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-[#4338ca] text-white text-[12px] font-bold">
                    {member.avatar}
                  </div>
                  <div>
                    <div className="text-[14px] font-semibold text-slate-900">
                      {member.name}
                    </div>
                    <div className="text-[12px] text-slate-500">
                      {member.email}
                    </div>
                  </div>
                </div>
              </td>
              <td className="px-6 py-4">
                <RoleBadge role={member.role} />
              </td>
              <td className="px-6 py-4">
                <StatusBadge status={member.status} />
              </td>
              <td className="px-6 py-4 text-center">
                <button className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-slate-500 hover:bg-slate-100">
                  ⋮
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="border-t border-slate-100 bg-slate-50 px-6 py-3 text-[13px] text-slate-600">
        Showing 1-3 of {members.length} members
      </div>
    </div>
  );
}

function ModulePermissionsCard({
  permissions,
}: {
  permissions: ModulePermission[];
}) {
  const [permissionsState, setPermissionsState] = useState<
    Record<string, ModulePermission>
  >(permissions.reduce((acc, p) => ({ ...acc, [p.id]: p }), {}));

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5">
      <h3 className="text-[15px] font-semibold text-slate-900 mb-4">
        Module Permissions
      </h3>
      <p className="text-[13px] text-slate-600 mb-5">
        Select a role to configure granular access across modules.
      </p>

      <div className="space-y-3">
        {permissions.map((perm) => (
          <div
            key={perm.id}
            className="flex items-center justify-between rounded-lg border border-slate-100 bg-slate-50 p-3"
          >
            <span className="text-[14px] font-medium text-slate-800">
              {perm.name}
            </span>
            <div className="flex items-center gap-2">
              <PermissionToggle enabled={perm.read} />
              <span className="text-[12px] text-slate-500">Read</span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-5 flex gap-3">
        <button className="flex-1 rounded-lg border border-slate-200 px-4 py-2.5 text-[14px] font-semibold text-slate-700 hover:bg-slate-50 transition">
          Reset
        </button>
        <button className="flex-1 rounded-lg bg-[#4338ca] px-4 py-2.5 text-[14px] font-semibold text-white hover:bg-[#3f2fd6] transition">
          Save Changes
        </button>
      </div>
    </div>
  );
}

export function TeamPage({ accessControl }: TeamPageProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [query, setQuery] = useState("");

  return (
    <div className="flex h-screen bg-slate-50">
      <TeamSidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex flex-1 flex-col overflow-hidden">
        <TeamNavbar
          query={query}
          onOpenSidebar={() => setSidebarOpen(true)}
          onQueryChange={setQuery}
        />

        <main className="flex-1 overflow-y-auto">
          <div className="space-y-6 p-4 sm:p-6 lg:p-8">
            {/* Header */}
            <div className="flex items-start justify-between gap-4">
              <div>
                <h1 className="text-[28px] font-bold text-slate-900">
                  Team Access Control
                </h1>
                <p className="mt-1 text-[15px] text-slate-600">
                  Manage member roles, permissions, and security policies.
                </p>
              </div>
              <button className="inline-flex items-center gap-2 rounded-lg bg-[#4338ca] px-4 py-2.5 text-[14px] font-semibold text-white hover:bg-[#3f2fd6] transition whitespace-nowrap">
                <span>👤</span>
                Invite Members
              </button>
            </div>

            {/* Main Content */}
            <div className="grid gap-6 lg:grid-cols-3">
              {/* Active Members */}
              <div className="lg:col-span-2">
                <div className="mb-4 flex items-center justify-between">
                  <div>
                    <h2 className="text-[18px] font-semibold text-slate-900">
                      Active Members
                    </h2>
                    <p className="mt-1 text-[13px] text-slate-600">
                      {accessControl.totalMembers} total members in workspace
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <button className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 hover:bg-slate-100">
                      🔍
                    </button>
                    <button className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 hover:bg-slate-100">
                      ⬇
                    </button>
                  </div>
                </div>
                <ActiveMembersTable members={accessControl.members} />
              </div>

              {/* Module Permissions */}
              <div>
                <ModulePermissionsCard
                  permissions={accessControl.permissions}
                />
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
