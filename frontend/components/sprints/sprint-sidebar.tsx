"use client";

import type { ComponentType } from "react";
import Link from "next/link";
import type { SprintSidebarItem } from "@/lib/sprints/types";
import {
  AIIcon,
  AnalyticsIcon,
  DashboardIcon,
  HelpIcon,
  MenuIcon,
  ProjectIcon,
  SettingsIcon,
  SprintIcon,
  TeamIcon,
  TasksIcon,
} from "./sprint-icons";

type SprintSidebarProps = {
  open: boolean;
  onClose: () => void;
  items: SprintSidebarItem[];
};

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

export function SprintSidebar({ open, onClose, items }: SprintSidebarProps) {
  return (
    <>
      <div
        className={`fixed inset-0 z-40 bg-slate-950/35 transition-opacity lg:hidden ${
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
            <div className="inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-[#4338ca] text-white">
              <span className="text-xl font-bold">B</span>
            </div>
            <div>
              <p className="text-[18px] leading-none font-bold tracking-[-0.03em] text-[#4338ca]">
                Bloom
              </p>
              <p className="text-sm font-medium text-slate-500">Engineering OS</p>
            </div>
          </div>

          <nav className="mt-8 space-y-2">
            {items.map((item) => {
              const Icon = iconMap[item.icon];

              return (
                <Link
                  key={item.label}
                  href={item.href}
                  className={`flex items-center gap-3 rounded-2xl px-4 py-3 text-[15px] font-medium transition ${
                    item.active
                      ? "bg-[#4338ca] text-white shadow-[0_10px_24px_rgba(67,56,202,0.2)]"
                      : "text-slate-600 hover:bg-white/80 hover:text-slate-900"
                  }`}
                >
                  <Icon className="h-5 w-5 shrink-0" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>

          <div className="mt-auto space-y-3 border-t border-slate-300/70 pt-5">
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
