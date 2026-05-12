"use client";

import type { ComponentType } from "react";
import { useMemo, useState } from "react";
import Link from "next/link";
import {
  AIGlyph,
  AnalyticsGlyph,
  BellIcon,
  BlockGlyph,
  CheckGlyph,
  DashboardGlyph,
  FlameGlyph,
  HelpIcon,
  LogoMarkIcon,
  ProjectGlyph,
  SearchIcon,
  SettingsGlyph,
  SidebarToggleIcon,
  SparkleGlyph,
  SprintGlyph,
  TeamGlyph,
  TasksGlyph,
  TrendGlyph,
} from "./icons";
import type { DashboardOverview, NotificationItem, StatCard } from "@/lib/dashboard/types";
import { dashboardNavItems } from "@/lib/dashboard/mock-data";

import { AppLayout } from "@/components/layout/app-layout";

type DashboardShellProps = {
  overview: DashboardOverview;
};

export function DashboardShell({ overview }: DashboardShellProps) {
  return (
    <AppLayout title="Dashboard Overview">
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.55fr)_minmax(300px,0.9fr)]">
        <section className="space-y-6">
          <StatsGrid stats={overview.stats} />
          <div className="grid gap-6 lg:grid-cols-[minmax(0,1.6fr)_minmax(280px,0.75fr)]">
            <SprintChartCard
              title={overview.sprint.title}
              subtitle={overview.sprint.subtitle}
              bars={overview.sprint.bars}
            />
            <NotificationsPanel notifications={overview.notifications} />
          </div>
        </section>
        <aside className="space-y-6">
          <ProfileCard />
          <AIModulePanel />
        </aside>
      </div>
    </AppLayout>
  );
}

function Sidebar({
  open,
  onClose,
  navIcons,
}: {
  open: boolean;
  onClose: () => void;
  navIcons: Record<string, ComponentType<{ className?: string }>>;
}) {
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
            <LogoMarkIcon className="h-10 w-10" />
            <div>
              <p className="text-[18px] font-bold tracking-[-0.02em] text-[#4338ca]">Bloom</p>
              <p className="text-sm font-medium text-slate-500">AI Productivity</p>
            </div>
          </div>

          <nav className="mt-8 space-y-2">
            {dashboardNavItems.map((item) => {
              const Icon = navIcons[item.icon];
              const active = item.active;
              return (
                <Link
                  key={item.label}
                  href={item.href}
                  className={`flex items-center gap-3 rounded-2xl px-4 py-3 text-[15px] font-medium transition ${
                    active
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
            <Link href="/support" className="flex items-center gap-3 rounded-2xl px-4 py-3 text-[15px] font-medium text-slate-600 hover:bg-white/70">
              <HelpIcon className="h-5 w-5" />
              <span>Support</span>
            </Link>
            <Link href="/logout" className="flex items-center gap-3 rounded-2xl px-4 py-3 text-[15px] font-medium text-slate-600 hover:bg-white/70">
              <SidebarToggleIcon className="h-5 w-5 rotate-180" />
              <span>Sign Out</span>
            </Link>
          </div>
        </div>
      </aside>
    </>
  );
}

function Topbar({ onMenuClick }: { onMenuClick: () => void }) {
  return (
    <header className="flex h-[84px] items-center gap-4 border-b border-slate-200 bg-white px-4 sm:px-6 lg:px-8">
      <button
        type="button"
        onClick={onMenuClick}
        className="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 text-slate-600 lg:hidden"
        aria-label="Open sidebar"
      >
        <SidebarToggleIcon className="h-5 w-5" />
      </button>
      <div className="min-w-0 flex-1">
        <h1 className="truncate text-[26px] font-semibold tracking-[-0.03em] text-slate-800 sm:text-[32px]">
          Dashboard Overview
        </h1>
      </div>
      <div className="hidden w-full max-w-[clamp(220px,24vw,360px)] flex-1 items-center rounded-2xl border border-[#e5def7] bg-[#f4eefc] px-4 py-3 text-slate-400 shadow-[0_1px_0_rgba(15,23,42,0.02)] lg:flex">
        <SearchIcon className="h-5 w-5 shrink-0" />
        <input
          aria-label="Search projects"
          placeholder="Search projects..."
          className="ml-3 w-full border-0 bg-transparent text-[15px] text-slate-700 placeholder:text-slate-400 focus:outline-none"
        />
      </div>
      <button className="hidden h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 text-slate-600 sm:inline-flex" aria-label="Notifications">
        <BellIcon className="h-5 w-5" />
      </button>
      <button className="hidden h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 text-slate-600 sm:inline-flex" aria-label="Help">
        <HelpIcon className="h-5 w-5" />
      </button>
      <button className="inline-flex h-11 items-center gap-2 rounded-2xl border border-[#e3dbf9] bg-[#f4efff] px-4 text-[15px] font-semibold text-[#4f46e5] shadow-[0_10px_24px_rgba(79,70,229,0.12)]">
        <SparkleGlyph className="h-4 w-4" />
        <span className="hidden sm:inline">AI Assistant</span>
      </button>
      <div className="h-11 w-11 rounded-full bg-[radial-gradient(circle_at_30%_30%,#374151,#0f172a)] shadow-[0_8px_18px_rgba(15,23,42,0.2)]" />
    </header>
  );
}

function StatsGrid({ stats }: { stats: StatCard[] }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {stats.map((stat) => (
        <StatCard key={stat.title} stat={stat} />
      ))}
    </div>
  );
}

function StatCard({ stat }: { stat: StatCard }) {
  const iconMap = {
    trend: TrendGlyph,
    check: CheckGlyph,
    flame: FlameGlyph,
    block: BlockGlyph,
  };
  const Icon = iconMap[stat.icon as keyof typeof iconMap];
  return (
    <article className="rounded-[22px] border border-slate-200 bg-white px-5 py-5 shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
      <div className={`inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br ${stat.accent} text-white`}>
        <Icon className="h-5 w-5" />
      </div>
      <div className="mt-6 flex flex-wrap items-end gap-x-2 gap-y-1">
        <p className="text-[32px] font-semibold leading-none tracking-[-0.04em] text-slate-800 sm:text-[36px]">{stat.value}</p>
        <span className={`pb-1 text-[14px] font-semibold sm:text-[15px] ${stat.deltaDirection === "up" ? "text-emerald-500" : "text-rose-500"}`}>
          {stat.delta}
        </span>
      </div>
      <p className="mt-3 text-[14px] font-medium text-slate-600 sm:text-[15px]">{stat.description}</p>
    </article>
  );
}

function SprintChartCard({
  title,
  subtitle,
  bars,
}: {
  title: string;
  subtitle: string;
  bars: DashboardOverview["sprint"]["bars"];
}) {
  return (
    <section className="overflow-hidden rounded-[24px] border border-slate-200 bg-white shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
      <div className="flex flex-col gap-4 border-b border-slate-200 px-5 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <div>
          <h2 className="text-[22px] font-semibold tracking-[-0.03em] text-slate-800 sm:text-[24px]">{title}</h2>
          <p className="text-[14px] text-slate-500 sm:text-[15px]">{subtitle}</p>
        </div>
        <button className="self-start rounded-2xl bg-[#f0ebff] px-4 py-3 text-[14px] font-semibold text-slate-700">
          Details
        </button>
      </div>
      <div className="px-4 py-6 sm:px-6">
        <div className="flex h-[220px] items-end gap-2 rounded-[20px] bg-[linear-gradient(180deg,#ffffff_0%,#fbfbff_100%)] px-2 pb-6 pt-5 sm:h-[320px] sm:gap-3 sm:px-3 sm:pb-8 sm:pt-6">
          {bars.map((bar) => (
            <div key={bar.label} className="flex flex-1 flex-col items-center gap-3 sm:gap-4">
              <div className="flex h-full w-full items-end justify-center">
                <div
                  className={`w-full max-w-[106px] rounded-t-[4px] ${
                    bar.active ? "bg-[#3f2fd6]" : "bg-[#e8e4f6]"
                  }`}
                  style={{ height: `${Math.max(bar.value, 12)}%` }}
                />
              </div>
              <span className={`text-[13px] font-medium sm:text-[14px] ${bar.active ? "text-[#3f2fd6]" : "text-slate-600"}`}>
                {bar.label}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function NotificationsPanel({ notifications }: { notifications: NotificationItem[] }) {
  return (
    <section className="overflow-hidden rounded-[24px] border border-[#e0daf5] bg-[linear-gradient(180deg,#fbf9ff_0%,#f7f4ff_100%)] shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
      <div className="border-b border-[#e5def7] px-5 py-5">
        <h2 className="text-[22px] font-semibold tracking-[-0.03em] text-slate-800 sm:text-[24px]">AI Insights</h2>
      </div>
      <div className="space-y-4 px-5 py-5">
        {notifications.length ? (
          notifications.map((notification) => <NotificationCard key={notification.id} notification={notification} />)
        ) : (
          <EmptyState title="No insights yet" description="AI insights will show up here once the pipeline is connected." />
        )}
      </div>
      <div className="px-5 pb-5">
        <button className="w-full rounded-2xl bg-[#3f2fd6] px-4 py-3 text-[14px] font-semibold text-white shadow-[0_12px_24px_rgba(63,47,214,0.24)] sm:text-[15px]">
          View Full Analysis
        </button>
      </div>
    </section>
  );
}

function NotificationCard({ notification }: { notification: NotificationItem }) {
  const toneMap = {
    info: "border-[#e4e0f8] bg-white text-[#6b4ce6]",
    warning: "border-[#f3dfb9] bg-white text-[#d97706]",
    success: "border-[#d6f0df] bg-white text-[#10b981]",
  };
  return (
    <article className={`rounded-[16px] border px-4 py-4 shadow-[0_8px_20px_rgba(15,23,42,0.04)] ${toneMap[notification.tone]}`}>
      <div className="flex items-start gap-3">
        <div className="mt-1 h-3 w-3 rounded-full bg-current" />
        <div className="min-w-0">
          <h3 className="text-[16px] font-semibold tracking-[-0.02em] text-slate-800">{notification.title}</h3>
          <p className="mt-1 text-[14px] leading-6 text-slate-600">{notification.description}</p>
        </div>
      </div>
    </article>
  );
}

function ProfileCard() {
  return (
    <section className="rounded-[24px] border border-slate-200 bg-white p-5 shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
      <div className="flex items-center gap-4">
        <div className="h-14 w-14 rounded-full bg-[radial-gradient(circle_at_35%_35%,#334155,#0f172a)]" />
        <div className="min-w-0">
          <p className="text-[18px] font-semibold tracking-[-0.02em] text-slate-800">Jordan Lee</p>
          <p className="text-[14px] text-slate-500">Engineering Manager</p>
        </div>
      </div>
      <div className="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-1">
        <MiniStat label="Projects" value="12" />
        <MiniStat label="Team" value="24" />
      </div>
    </section>
  );
}

function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[18px] border border-slate-200 bg-slate-50 px-4 py-4">
      <p className="text-[13px] font-medium text-slate-500">{label}</p>
      <p className="mt-1 text-[22px] font-semibold tracking-[-0.03em] text-slate-800">{value}</p>
    </div>
  );
}

function AIModulePanel() {
  return (
    <section className="rounded-[24px] border border-[#e0daf5] bg-[linear-gradient(180deg,#faf7ff_0%,#f3efff_100%)] p-5 shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
      <div className="flex items-center gap-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[#4338ca] text-white">
          <SparkleGlyph className="h-5 w-5" />
        </div>
        <div>
          <p className="text-[18px] font-semibold tracking-[-0.03em] text-slate-800 sm:text-[20px]">AI Assistant</p>
          <p className="text-[13px] text-slate-500 sm:text-[14px]">Productivity recommendations</p>
        </div>
      </div>
      <div className="mt-5 space-y-3">
        <InfoCard title="Sprint prediction" body="The team is on track to finish all core tasks one day early." />
        <InfoCard title="Workload alert" body="Sarah has taken 3 complex tickets simultaneously. Consider reassigning DEV-402." tone="warning" />
      </div>
    </section>
  );
}

function InfoCard({ title, body, tone = "info" }: { title: string; body: string; tone?: "info" | "warning" }) {
  const styles = tone === "warning" ? "text-amber-500" : "text-[#6b4ce6]";
  return (
    <article className="rounded-[18px] border border-slate-200 bg-white p-4 shadow-[0_8px_20px_rgba(15,23,42,0.04)]">
      <p className={`text-[14px] font-semibold uppercase tracking-[0.16em] ${styles}`}>{title}</p>
      <p className="mt-2 text-[15px] leading-6 text-slate-600">{body}</p>
    </article>
  );
}

function EmptyState({ title, description }: { title: string; description: string }) {
  return (
    <div className="rounded-[20px] border border-dashed border-slate-300 bg-slate-50 px-6 py-8 text-center">
      <p className="text-[16px] font-semibold text-slate-700">{title}</p>
      <p className="mt-2 text-[14px] leading-6 text-slate-500">{description}</p>
    </div>
  );
}
