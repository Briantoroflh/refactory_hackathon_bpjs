"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
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
  SprintGlyph,
  TasksGlyph,
  TeamGlyph,
} from "@/components/dashboard/icons";
import {
  fetchCurrentProfile,
  updateCurrentProfile,
  type ProfileUser,
} from "@/lib/profile/api";

type NavItem = {
  label: string;
  href: string;
  icon: (props: { className?: string }) => JSX.Element;
  active?: boolean;
};

const navItems: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: DashboardGlyph },
  { label: "Project", href: "/projects", icon: ProjectGlyph },
  { label: "Sprint", href: "/sprints", icon: SprintGlyph },
  { label: "Tasks", href: "/tasks", icon: TasksGlyph },
  { label: "Analytics", href: "/analytics", icon: AnalyticsGlyph },
  { label: "AI Assistant", href: "/ai", icon: AIGlyph },
  { label: "Team", href: "/team", icon: TeamGlyph },
  { label: "Profile", href: "/profile", icon: ProfileGlyph, active: true },
  { label: "Settings", href: "/settings", icon: SettingsGlyph },
];

export function ProfilePage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [profile, setProfile] = useState<ProfileUser | null>(null);
  const [fullNameDraft, setFullNameDraft] = useState("");
  const [isEditingName, setIsEditingName] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadProfile = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await fetchCurrentProfile();
      setProfile(data);
      setFullNameDraft(data.full_name ?? "");
    } catch (loadError) {
      const message =
        loadError instanceof Error
          ? loadError.message
          : "Failed to load profile";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  const initials = useMemo(() => {
    if (!profile) {
      return "NA";
    }

    const source = profile.full_name?.trim() || profile.email;
    return source
      .split(" ")
      .filter(Boolean)
      .slice(0, 2)
      .map((word) => word[0]?.toUpperCase() ?? "")
      .join("");
  }, [profile]);

  const onSaveName = useCallback(async () => {
    if (!profile) {
      return;
    }

    const trimmed = fullNameDraft.trim();
    if (!trimmed) {
      setError("Full name cannot be empty");
      return;
    }

    setIsSaving(true);
    setError(null);
    setSuccess(null);

    try {
      const updated = await updateCurrentProfile({ full_name: trimmed });
      setProfile(updated);
      setFullNameDraft(updated.full_name ?? "");
      setIsEditingName(false);
      setSuccess("Profile updated successfully");
    } catch (saveError) {
      const message =
        saveError instanceof Error
          ? saveError.message
          : "Failed to update profile";
      setError(message);
    } finally {
      setIsSaving(false);
    }
  }, [fullNameDraft, profile]);

  return (
    <div className="flex h-screen bg-slate-50">
      <ProfileSidebar
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex h-[82px] items-center gap-4 border-b border-slate-200 bg-white px-4 sm:px-6 lg:px-8">
          <button
            type="button"
            onClick={() => setSidebarOpen(true)}
            className="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 text-slate-600 lg:hidden"
            aria-label="Open sidebar"
          >
            <SidebarToggleIcon className="h-5 w-5" />
          </button>

          <div className="hidden items-center gap-2 text-[15px] font-semibold text-slate-500 md:flex">
            <span>Account</span>
            <span className="text-slate-300">/</span>
            <span className="text-[#3f2fd6]">Profile</span>
          </div>

          <div className="ml-auto flex w-full max-w-[320px] items-center rounded-full border border-[#e5def7] bg-[#f3ecfc] px-4 py-2.5 text-slate-400">
            <SearchIcon className="h-5 w-5 shrink-0" />
            <input
              aria-label="Search profile settings"
              placeholder="Search profile..."
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              className="ml-3 w-full border-0 bg-transparent text-[15px] text-slate-700 placeholder:text-slate-400 focus:outline-none"
            />
          </div>

          <div className="hidden items-center gap-3 sm:flex">
            <button
              className="inline-flex h-11 w-11 items-center justify-center rounded-full text-slate-500 hover:bg-slate-100"
              aria-label="Notifications"
            >
              <BellIcon className="h-5 w-5" />
            </button>
            <button
              className="inline-flex h-11 w-11 items-center justify-center rounded-full text-slate-500 hover:bg-slate-100"
              aria-label="Help"
            >
              <HelpIcon className="h-5 w-5" />
            </button>
          </div>

          <div className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-[#4338ca] text-[12px] font-bold text-white">
            {initials}
          </div>
        </header>

        <main className="flex-1 overflow-y-auto">
          <div className="space-y-6 p-4 sm:p-6 lg:p-8">
            <div>
              <h1 className="text-[28px] font-bold text-slate-900">
                My Profile
              </h1>
              <p className="mt-1 text-[15px] text-slate-600">
                Manage your account information connected to backend
                authentication.
              </p>
            </div>

            {error ? (
              <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-[14px] text-rose-700">
                {error}
              </div>
            ) : null}

            {success ? (
              <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-[14px] text-emerald-700">
                {success}
              </div>
            ) : null}

            {isLoading ? (
              <div className="grid gap-4 md:grid-cols-2">
                <div className="h-52 rounded-2xl border border-slate-200 bg-white" />
                <div className="h-52 rounded-2xl border border-slate-200 bg-white" />
              </div>
            ) : profile ? (
              <div className="grid gap-6 xl:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)]">
                <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                  <div className="mb-6 flex items-center justify-between gap-3">
                    <div>
                      <h2 className="text-[20px] font-semibold text-slate-900">
                        Identity
                      </h2>
                      <p className="text-[14px] text-slate-500">
                        Data sourced from backend user service.
                      </p>
                    </div>
                    <button
                      onClick={loadProfile}
                      className="rounded-lg border border-slate-200 px-3 py-2 text-[13px] font-medium text-slate-700 hover:bg-slate-100"
                    >
                      Refresh
                    </button>
                  </div>

                  <dl className="space-y-4">
                    <div className="grid gap-1">
                      <dt className="text-[13px] font-medium uppercase tracking-wide text-slate-500">
                        User ID
                      </dt>
                      <dd className="text-[16px] font-semibold text-slate-900">
                        {profile.user_id}
                      </dd>
                    </div>

                    <div className="grid gap-1">
                      <dt className="text-[13px] font-medium uppercase tracking-wide text-slate-500">
                        Email
                      </dt>
                      <dd className="text-[16px] font-semibold text-slate-900">
                        {profile.email}
                      </dd>
                    </div>

                    <div className="grid gap-1">
                      <dt className="text-[13px] font-medium uppercase tracking-wide text-slate-500">
                        Full Name
                      </dt>
                      <dd>
                        {isEditingName ? (
                          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
                            <input
                              value={fullNameDraft}
                              onChange={(event) =>
                                setFullNameDraft(event.target.value)
                              }
                              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-[15px] text-slate-800 focus:border-[#4338ca] focus:outline-none"
                            />
                            <div className="flex items-center gap-2">
                              <button
                                onClick={onSaveName}
                                disabled={isSaving}
                                className="rounded-lg bg-[#4338ca] px-3 py-2 text-[13px] font-semibold text-white disabled:cursor-not-allowed disabled:opacity-70"
                              >
                                {isSaving ? "Saving..." : "Save"}
                              </button>
                              <button
                                onClick={() => {
                                  setIsEditingName(false);
                                  setFullNameDraft(profile.full_name ?? "");
                                  setError(null);
                                }}
                                className="rounded-lg border border-slate-300 px-3 py-2 text-[13px] font-medium text-slate-700 hover:bg-slate-100"
                              >
                                Cancel
                              </button>
                            </div>
                          </div>
                        ) : (
                          <div className="flex items-center justify-between gap-3">
                            <span className="text-[16px] font-semibold text-slate-900">
                              {profile.full_name || "No full name set"}
                            </span>
                            <button
                              onClick={() => {
                                setIsEditingName(true);
                                setSuccess(null);
                                setError(null);
                              }}
                              className="rounded-lg border border-slate-300 px-3 py-2 text-[13px] font-medium text-slate-700 hover:bg-slate-100"
                            >
                              Edit
                            </button>
                          </div>
                        )}
                      </dd>
                    </div>
                  </dl>
                </section>

                <aside className="space-y-6">
                  <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                    <h3 className="text-[16px] font-semibold text-slate-900">
                      Account Status
                    </h3>
                    <p className="mt-4 inline-flex items-center gap-2 rounded-full px-3 py-1 text-[13px] font-semibold text-white bg-emerald-500">
                      <span className="h-2 w-2 rounded-full bg-white" />
                      {profile.is_active ? "Active" : "Inactive"}
                    </p>
                    <div className="mt-5 border-t border-slate-100 pt-4">
                      <p className="text-[13px] text-slate-500">Last Login</p>
                      <p className="mt-1 text-[14px] font-medium text-slate-800">
                        {profile.last_login
                          ? new Date(profile.last_login).toLocaleString()
                          : "No login history available"}
                      </p>
                    </div>
                  </section>

                  <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                    <h3 className="text-[16px] font-semibold text-slate-900">
                      Quick Actions
                    </h3>
                    <div className="mt-4 space-y-3">
                      <Link
                        href="/settings"
                        className="block rounded-lg border border-slate-200 px-4 py-3 text-[14px] font-medium text-slate-700 hover:bg-slate-100"
                      >
                        Open System Settings
                      </Link>
                      <Link
                        href="/dashboard"
                        className="block rounded-lg border border-slate-200 px-4 py-3 text-[14px] font-medium text-slate-700 hover:bg-slate-100"
                      >
                        Back to Dashboard
                      </Link>
                    </div>
                  </section>
                </aside>
              </div>
            ) : (
              <div className="rounded-2xl border border-slate-200 bg-white p-6 text-[15px] text-slate-600">
                Profile data is not available.
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

function ProfileSidebar({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  return (
    <>
      {open ? (
        <div
          className="fixed inset-0 z-40 bg-black/20 lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      ) : null}

      <aside
        className={`fixed left-0 top-0 z-50 flex h-screen w-[280px] flex-col border-r border-slate-200 bg-white transition-transform duration-300 ease-in-out lg:static lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex h-[88px] items-center justify-between border-b border-slate-100 px-4 sm:px-6">
          <Link href="/profile" className="flex items-center gap-2">
            <LogoMarkIcon className="h-10 w-10" />
            <div>
              <div className="text-[15px] font-bold text-slate-800">Bloom</div>
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

        <nav className="flex-1 overflow-y-auto px-3 py-4">
          <div className="space-y-1">
            {navItems.map((item) => {
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

        <div className="border-t border-slate-200 px-3 py-4">
          <Link
            href="/support"
            className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-[15px] font-medium text-slate-700 hover:bg-slate-100"
          >
            <HelpIcon className="h-5 w-5" />
            <span>Support</span>
          </Link>
        </div>
      </aside>
    </>
  );
}

function ProfileGlyph({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
      className={className}
    >
      <circle cx="12" cy="8" r="3" stroke="currentColor" strokeWidth="1.7" />
      <path
        d="M5.5 19a6.5 6.5 0 0 1 13 0"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
      />
    </svg>
  );
}
