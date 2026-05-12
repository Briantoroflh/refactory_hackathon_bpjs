"use client";

import type { ComponentType } from "react";
import Link from "next/link";
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

type TeamSidebarProps = {
  open: boolean;
  onClose: () => void;
};

type NavItem = {
  label: string;
  href: string;
  icon: ComponentType<{ className?: string }>;
  active?: boolean;
};

const navigationItems: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: DashboardGlyph },
  { label: "Project", href: "/projects", icon: ProjectGlyph },
  { label: "Sprint", href: "/sprints", icon: SprintGlyph },
  { label: "Tasks", href: "/tasks", icon: TasksGlyph },
  { label: "Analytics", href: "/analytics", icon: AnalyticsGlyph },
  { label: "AI Assistant", href: "/ai", icon: AIGlyph },
  { label: "Team", href: "/team", icon: TeamGlyph, active: true },
  { label: "Settings", href: "/settings", icon: SettingsGlyph },
];

export function TeamSidebar({ open, onClose }: TeamSidebarProps) {
  return (
    <>
      {/* Mobile backdrop */}
      {open && (
        <div
          className="fixed inset-0 z-40 bg-black/20 lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed left-0 top-0 z-50 flex h-screen w-[280px] flex-col border-r border-slate-200 bg-white transition-transform duration-300 ease-in-out lg:static lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Header */}
        <div className="flex h-[88px] items-center justify-between border-b border-slate-100 px-4 sm:px-6">
          <Link href="/team" className="flex items-center gap-2">
            <LogoMarkIcon className="h-10 w-10" />
            <div>
              <div className="text-[15px] font-bold text-slate-800">
                SprintFlow
              </div>
              <div className="text-[12px] font-medium text-slate-500">
                AI Productivity
              </div>
            </div>
          </Link>
          <button
            onClick={onClose}
            className="inline-flex lg:hidden"
            aria-label="Close sidebar"
          >
            <SidebarToggleIcon className="h-5 w-5 rotate-180" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto px-3 py-4">
          <div className="space-y-1">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = item.active;
              return (
                <Link
                  key={item.label}
                  href={item.href}
                  className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-[15px] font-medium transition ${
                    isActive
                      ? "bg-[#4338ca] text-white"
                      : "text-slate-700 hover:bg-slate-100"
                  }`}
                >
                  <Icon className="h-5 w-5 shrink-0" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </div>
        </nav>

        {/* Footer */}
        <div className="border-t border-slate-200 px-3 py-4">
          <button className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-[15px] font-medium text-slate-700 hover:bg-slate-100">
            <HelpIcon className="h-5 w-5" />
            <span>Support</span>
          </button>
          <button className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-[15px] font-medium text-slate-700 hover:bg-slate-100">
            <SidebarToggleIcon className="h-5 w-5 rotate-180" />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>
    </>
  );
}
