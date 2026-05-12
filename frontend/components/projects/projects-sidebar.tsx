"use client";

import type { ComponentType } from "react";
import Link from "next/link";
import { projectSidebarItems } from "@/lib/projects/mock-data";
import {
  DashboardGlyph,
  ProjectGlyph,
  SprintGlyph,
  TasksGlyph,
  AnalyticsGlyph,
  AIGlyph,
  TeamGlyph,
  SettingsGlyph,
  HelpIcon,
  SidebarToggleIcon,
  LogoMarkIcon,
} from "@/components/dashboard/icons";

type ProjectsSidebarProps = {
  open: boolean;
  onClose: () => void;
};

const iconMap: Record<string, ComponentType<{ className?: string }>> = {
  dashboard: DashboardGlyph,
  project: ProjectGlyph,
  sprint: SprintGlyph,
  tasks: TasksGlyph,
  analytics: AnalyticsGlyph,
  ai: AIGlyph,
  team: TeamGlyph,
  settings: SettingsGlyph,
};

export function ProjectsSidebar({ open, onClose }: ProjectsSidebarProps) {
  return (
    <>
      <div
        className={`fixed inset-0 z-40 bg-slate-950/30 transition-opacity lg:hidden ${
          open ? "opacity-100" : "pointer-events-none opacity-0"
        }`}
        onClick={onClose}
        aria-hidden="true"
      />
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-[286px] border-r border-[#e7e2f3] bg-[#f3f1fb] p-5 transition-transform duration-300 lg:static lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        }`}
      >
        <div className="flex h-full flex-col">
          <div className="flex items-center gap-3 px-1 py-2">
            <LogoMarkIcon className="h-10 w-10" />
            <div>
              <p className="text-[18px] font-bold tracking-[-0.02em] text-[#4338ca]">
                Bloom
              </p>
              <p className="text-sm font-medium text-slate-500">
                AI Productivity
              </p>
            </div>
          </div>

          <nav className="mt-8 space-y-2">
            {projectSidebarItems.map((item) => {
              const Icon = iconMap[item.icon];
              return (
                <Link
                  key={item.label}
                  href={item.href}
                  className={`flex items-center gap-3 rounded-2xl px-4 py-3 text-[15px] font-medium transition ${
                    "active" in item && item.active
                      ? "bg-[#4338ca] text-white shadow-[0_12px_24px_rgba(67,56,202,0.22)]"
                      : "text-slate-600 hover:bg-white/70 hover:text-slate-900"
                  }`}
                >
                  <Icon className="h-5 w-5 shrink-0" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>

          <div className="mt-auto space-y-3 border-t border-slate-200/70 pt-5">
            <Link
              href="/support"
              className="flex items-center gap-3 rounded-2xl px-4 py-3 text-[15px] font-medium text-slate-600 hover:bg-white/70"
            >
              <HelpIcon className="h-5 w-5" />
              <span>Support</span>
            </Link>
            <Link
              href="/logout"
              className="flex items-center gap-3 rounded-2xl px-4 py-3 text-[15px] font-medium text-slate-600 hover:bg-white/70"
            >
              <SidebarToggleIcon className="h-5 w-5 rotate-180" />
              <span>Sign Out</span>
            </Link>
          </div>
        </div>
      </aside>
    </>
  );
}
