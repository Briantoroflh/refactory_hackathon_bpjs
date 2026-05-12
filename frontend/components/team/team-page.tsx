"use client";

import React, { useState } from "react";
import { AppLayout } from "@/components/layout/app-layout";
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
        variants[status as keyof typeof variants] || ""
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
        variants[role as keyof typeof variants] || ""
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
    <div className="rounded-[24px] border border-slate-200 bg-white overflow-hidden shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
      <table className="w-full">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50/50">
            <th className="px-6 py-4 text-left text-[12px] font-bold text-slate-500 uppercase tracking-widest">
              Name
            </th>
            <th className="px-6 py-4 text-left text-[12px] font-bold text-slate-500 uppercase tracking-widest">
              Role
            </th>
            <th className="px-6 py-4 text-left text-[12px] font-bold text-slate-500 uppercase tracking-widest">
              Status
            </th>
            <th className="px-6 py-4 text-center text-[12px] font-bold text-slate-500 uppercase tracking-widest">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {members.map((member) => (
            <tr
              key={member.id}
              className="hover:bg-slate-50/50 transition-colors"
            >
              <td className="px-6 py-4">
                <div className="flex items-center gap-3">
                  <div className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-[#4338ca] to-[#6366f1] text-white text-[12px] font-bold shadow-sm">
                    {member.avatar}
                  </div>
                  <div>
                    <div className="text-[14px] font-bold text-slate-900">
                      {member.name}
                    </div>
                    <div className="text-[12px] font-medium text-slate-500">
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
                <button className="inline-flex h-9 w-9 items-center justify-center rounded-xl text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition">
                  ⋮
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="border-t border-slate-50 bg-slate-50/50 px-6 py-4 text-[13px] font-medium text-slate-500">
        Showing {members.length} members in workspace
      </div>
    </div>
  );
}

function ModulePermissionsCard({
  permissions,
}: {
  permissions: ModulePermission[];
}) {
  return (
    <div className="rounded-[24px] border border-slate-200 bg-white p-6 shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
      <h3 className="text-[18px] font-bold text-slate-900 mb-2">
        Module Permissions
      </h3>
      <p className="text-[14px] font-medium text-slate-500 mb-6">
        Configure granular access across modules.
      </p>

      <div className="space-y-3">
        {permissions.map((perm) => (
          <div
            key={perm.id}
            className="flex items-center justify-between rounded-2xl border border-slate-100 bg-slate-50/50 p-4 hover:bg-white hover:border-[#4338ca]/20 transition-all group"
          >
            <span className="text-[14px] font-bold text-slate-700 group-hover:text-[#4338ca] transition-colors">
              {perm.name}
            </span>
            <div className="flex items-center gap-3">
              <span className="text-[12px] font-bold text-slate-400 uppercase tracking-wider">Read</span>
              <PermissionToggle enabled={perm.read} />
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8 flex gap-3">
        <button className="flex-1 rounded-2xl border border-slate-200 px-4 py-3 text-[14px] font-bold text-slate-600 hover:bg-slate-50 transition shadow-sm">
          Reset
        </button>
        <button className="flex-1 rounded-2xl bg-[#4338ca] px-4 py-3 text-[14px] font-bold text-white hover:bg-[#3f2fd6] transition shadow-[0_10px_24px_rgba(67,56,202,0.2)]">
          Save Changes
        </button>
      </div>
    </div>
  );
}

export function TeamPage({ accessControl }: TeamPageProps) {
  return (
    <AppLayout title="Team Access Control">
      <div className="space-y-6">
        {/* Header Extra */}
        <div className="flex items-start justify-between gap-4">
          <p className="text-[16px] font-medium text-slate-500 max-w-md">
            Manage member roles, permissions, and workspace security policies from a single dashboard.
          </p>
          <button className="inline-flex items-center gap-2 rounded-xl bg-[#4338ca] px-5 py-3 text-[14px] font-bold text-white hover:bg-[#3f2fd6] transition whitespace-nowrap shadow-[0_10px_24px_rgba(67,56,202,0.25)]">
            👤 Invite Members
          </button>
        </div>

        {/* Main Content */}
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Active Members */}
          <div className="lg:col-span-2">
            <div className="mb-4 flex items-center justify-between px-1">
              <div>
                <h2 className="text-[20px] font-bold tracking-tight text-slate-900">
                  Active Members
                </h2>
              </div>
              <div className="flex items-center gap-2">
                <button className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 bg-white hover:bg-slate-50 shadow-sm transition">
                  🔍
                </button>
                <button className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 bg-white hover:bg-slate-50 shadow-sm transition">
                  ⬇
                </button>
              </div>
            </div>
            <ActiveMembersTable members={accessControl.members} />
          </div>

          {/* Module Permissions */}
          <div>
            <div className="mb-4 px-1">
              <h2 className="text-[20px] font-bold tracking-tight text-slate-900">Permissions</h2>
            </div>
            <ModulePermissionsCard
              permissions={accessControl.permissions}
            />
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
