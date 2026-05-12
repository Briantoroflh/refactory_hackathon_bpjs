"use client";

import React, { useState, useMemo, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  AIGlyph,
  AnalyticsGlyph,
  BellIcon,
  DashboardGlyph,
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
} from "@/components/dashboard/icons";
import { fetchCurrentProfile, type ProfileUser } from "@/lib/profile/api";

type AppLayoutProps = {
  children: React.ReactNode;
  title?: string;
  breadcrumbs?: { label: string; href?: string }[];
  searchPlaceholder?: string;
};

export function AppLayout({ children, title, breadcrumbs, searchPlaceholder }: AppLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [user, setUser] = useState<ProfileUser | null>(null);
  const pathname = usePathname();

  useEffect(() => {
    async function loadUser() {
      try {
        const data = await fetchCurrentProfile();
        setUser(data);
      } catch {
        // Silently fail, header will show placeholder
      }
    }
    loadUser();
  }, []);

  const initials = useMemo(() => {
    if (!user) return "??";
    const source = user.full_name?.trim() || user.email;
    return source
      .split(" ")
      .filter(Boolean)
      .slice(0, 2)
      .map((word) => word[0]?.toUpperCase() ?? "")
      .join("");
  }, [user]);

  const navigationItems = [
    { label: "Dashboard", href: "/dashboard", icon: DashboardGlyph },
    { label: "Project", href: "/projects", icon: ProjectGlyph },
    { label: "Sprint", href: "/sprints", icon: SprintGlyph },
    { label: "Tasks", href: "/tasks", icon: TasksGlyph },
    { label: "Analytics", href: "/analytics", icon: AnalyticsGlyph },
    { label: "AI Assistant", href: "/ai", icon: AIGlyph },
    { label: "Team", href: "/team", icon: TeamGlyph },
    { label: "Settings", href: "/settings", icon: SettingsGlyph },
  ];

  return (
    <div className="min-h-screen bg-[#f3f5fb] text-slate-900">
      <div className="mx-auto flex min-h-screen w-full flex-col overflow-hidden bg-white lg:rounded-none xl:my-4 xl:rounded-[24px] xl:border xl:border-slate-200 xl:shadow-[0_10px_40px_rgba(15,23,42,0.08)]">
        <div className="flex flex-1 overflow-hidden">
          {/* Sidebar */}
          <>
            <div
              className={`fixed inset-0 z-40 bg-slate-950/30 transition-opacity lg:hidden ${
                sidebarOpen ? "opacity-100" : "pointer-events-none opacity-0"
              }`}
              onClick={() => setSidebarOpen(false)}
              aria-hidden="true"
            />
            <aside
              className={`fixed inset-y-0 left-0 z-50 w-[290px] border-r border-[#e8e4f6] bg-[#fbfbff] p-5 shadow-[8px_0_24px_rgba(15,23,42,0.08)] transition-transform duration-300 lg:static lg:z-auto lg:w-[clamp(240px,18vw,290px)] lg:translate-x-0 lg:shadow-none ${
                sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
              }`}
            >
              <div className="flex h-full flex-col">
                <div className="flex items-center gap-3 px-1 py-2">
                  <LogoMarkIcon className="h-10 w-10" />
                  <div>
                    <p className="text-[18px] font-bold tracking-[-0.02em] text-[#4338ca]">Bloom</p>
                    <p className="text-[12px] font-bold text-slate-400 uppercase tracking-widest">Team Analytics</p>
                  </div>
                </div>

                <nav className="mt-8 space-y-1.5">
                  {navigationItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = pathname.startsWith(item.href);
                    return (
                      <Link
                        key={item.label}
                        href={item.href}
                        className={`flex items-center gap-3 rounded-2xl px-4 py-3 text-[15px] font-bold transition-all ${
                          isActive
                            ? "bg-[#4338ca] text-white shadow-[0_12px_24px_rgba(67,56,202,0.25)]"
                            : "text-slate-500 hover:bg-slate-50 hover:text-slate-900"
                        }`}
                      >
                        <Icon className="h-5 w-5 shrink-0" />
                        <span>{item.label}</span>
                      </Link>
                    );
                  })}
                </nav>

                <div className="mt-auto space-y-1 border-t border-slate-100 pt-5">
                  <Link href="/support" className="flex items-center gap-3 rounded-2xl px-4 py-3 text-[15px] font-bold text-slate-500 hover:bg-slate-50">
                    <HelpIcon className="h-5 w-5" />
                    <span>Support</span>
                  </Link>
                  <Link href="/logout" className="flex items-center gap-3 rounded-2xl px-4 py-3 text-[15px] font-bold text-slate-500 hover:bg-slate-50">
                    <SidebarToggleIcon className="h-5 w-5 rotate-180" />
                    <span>Sign Out</span>
                  </Link>
                </div>
              </div>
            </aside>
          </>

          {/* Main Content */}
          <div className="flex min-w-0 flex-1 flex-col">
            {/* Topbar */}
            <header className="flex h-[100px] flex-col justify-center gap-1 border-b border-slate-100 bg-white px-4 sm:px-6 lg:px-8">
              <div className="flex items-center gap-4">
                <button
                  type="button"
                  onClick={() => setSidebarOpen(true)}
                  className="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 text-slate-600 lg:hidden"
                  aria-label="Open sidebar"
                >
                  <SidebarToggleIcon className="h-5 w-5" />
                </button>
                
                <div className="flex min-w-0 flex-1 flex-col">
                  {breadcrumbs && (
                    <nav className="flex items-center gap-1.5 text-[14px] font-bold text-slate-400 mb-1">
                      {breadcrumbs.map((crumb, i) => (
                        <React.Fragment key={crumb.label}>
                          {i > 0 && <span>›</span>}
                          <span className={i === breadcrumbs.length - 1 ? "text-[#4338ca]" : ""}>
                            {crumb.label}
                          </span>
                        </React.Fragment>
                      ))}
                    </nav>
                  )}
                  <h1 className="truncate text-[28px] font-bold tracking-tight text-slate-900">
                    {title || "Overview"}
                  </h1>
                </div>

                <div className="hidden w-full max-w-[360px] items-center rounded-full border border-slate-100 bg-slate-50 px-5 py-3 text-slate-400 shadow-sm lg:flex focus-within:ring-2 focus-within:ring-[#4338ca]/20 transition-all">
                  <SearchIcon className="h-5 w-5 shrink-0" />
                  <input
                    aria-label="Search"
                    placeholder={searchPlaceholder || (title ? `Search ${title.toLowerCase()}...` : "Search analytics...")}
                    className="ml-3 w-full border-0 bg-transparent text-[15px] font-medium text-slate-700 placeholder:text-slate-400 focus:outline-none"
                  />
                </div>

                <div className="flex items-center gap-3">
                  <button className="hidden h-11 w-11 items-center justify-center rounded-2xl text-slate-400 hover:bg-slate-50 hover:text-slate-600 sm:inline-flex" aria-label="Notifications">
                    <BellIcon className="h-5 w-5" />
                  </button>
                  <button className="hidden h-11 w-11 items-center justify-center rounded-2xl text-slate-400 hover:bg-slate-50 hover:text-slate-600 sm:inline-flex" aria-label="Help">
                    <HelpIcon className="h-5 w-5" />
                  </button>
                  <Link 
                    href="/profile"
                    className="h-11 w-11 rounded-full bg-[#4338ca] flex items-center justify-center text-[14px] font-bold text-white shadow-[0_8px_20px_rgba(67,56,202,0.3)] border-2 border-white hover:scale-105 transition-transform"
                    title={user?.full_name || user?.email || "Profile"}
                  >
                    {initials}
                  </Link>
                </div>
              </div>
            </header>

            <main className="flex-1 overflow-y-auto bg-[#f8f9fd] px-4 py-6 sm:px-6 lg:px-8">
              {children}
            </main>
          </div>
        </div>
      </div>
    </div>
  );
}
