"use client";

import type { ComponentType } from "react";
import Link from "next/link";
import {
  AIIcon,
  AnalyticsIcon,
  DashboardIcon,
  HelpIcon,
  LogoIcon,
  ProjectIcon,
  SettingsIcon,
  SprintIcon,
  TasksIcon,
  TeamIcon,
  MenuIcon,
} from "./ai-icons";

type AISidebarProps = {
  open: boolean;
  onClose: () => void;
};

const navItems = [
  { label: "Dashboard", href: "/dashboard", icon: "dashboard", active: false },
  { label: "Project", href: "/projects", icon: "project", active: false },
  { label: "Sprint", href: "/sprints", icon: "sprint", active: false },
  { label: "Tasks", href: "/tasks", icon: "tasks", active: false },
  { label: "Analytics", href: "/analytics", icon: "analytics", active: false },
  { label: "AI Assistant", href: "/ai", icon: "ai", active: true },
  { label: "Team", href: "/team", icon: "team", active: false },
  { label: "Settings", href: "/settings", icon: "settings", active: false },
];

const iconMap: Record<string, ComponentType<{ className?: string }>> = {
  dashboard: DashboardIcon,
  project: ProjectIcon,
  sprint: SprintIcon,
  tasks: TasksIcon,
  analytics: AnalyticsIcon,
  ai: AIIcon,
  team: TeamIcon,
  settings: SettingsIcon,
};

export function AISidebar({ open, onClose }: AISidebarProps) {
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
        className={`fixed inset-y-0 left-0 z-50 w-[290px] border-r border-[#e8e4f6] bg-[linear-gradient(180deg,#f7f2ff_0%,#f3eefc_100%)] p-5 shadow-[8px_0_24px_rgba(15,23,42,0.08)] transition-transform duration-300 lg:static lg:z-auto lg:w-[clamp(240px,18vw,290px)] lg:translate-x-0 lg:shadow-none ${
          open ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        }`}
      >
        <div className="flex h-full flex-col">
          <div className="flex items-center gap-3 px-1 py-2">
            <LogoIcon className="h-10 w-10" />
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
            {navItems.map((item) => {
              const Icon = iconMap[item.icon];
              return (
                <Link
                  key={item.label}
                  href={item.href}
                  className={`flex items-center gap-3 rounded-2xl px-4 py-3 text-[15px] font-medium transition ${
                    item.active
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
              <MenuIcon className="h-5 w-5 rotate-180" />
              <span>Sign Out</span>
            </Link>
          </div>
        </div>
      </aside>
    </>
  );
}
