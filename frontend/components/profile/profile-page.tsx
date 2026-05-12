"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  fetchCurrentProfile,
  updateCurrentProfile,
  type ProfileUser,
} from "@/lib/profile/api";
import { AppLayout } from "@/components/layout/app-layout";


export function ProfilePage() {
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
    <AppLayout 
      title="My Profile" 
      breadcrumbs={[{ label: "Account" }, { label: "Profile" }]}
      searchPlaceholder="Search your account..."
    >
      <div className="space-y-6">
        <div>
          <p className="mt-1 text-[15px] font-medium text-slate-500">
            Manage your account information connected to backend authentication.
          </p>
        </div>

        {error ? (
          <div className="rounded-2xl border border-rose-200 bg-rose-50 px-5 py-4 shadow-sm animate-in fade-in slide-in-from-top-2">
            <div className="flex items-center gap-3">
              <span className="text-xl">⚠️</span>
              <div>
                <p className="text-[14px] font-bold text-rose-700">{error}</p>
                {error.includes("token") || error.includes("authenticated") ? (
                  <Link 
                    href="/login" 
                    className="mt-1 inline-block text-[13px] font-bold text-rose-600 underline hover:text-rose-800"
                  >
                    Click here to sign in again
                  </Link>
                ) : null}
              </div>
            </div>
          </div>
        ) : null}

        {success ? (
          <div className="rounded-2xl border border-emerald-200 bg-emerald-50 px-5 py-4 text-[14px] font-bold text-emerald-700 shadow-sm animate-in fade-in slide-in-from-top-2">
            ✅ {success}
          </div>
        ) : null}

        {isLoading ? (
          <div className="grid gap-6 md:grid-cols-2">
            <div className="h-64 rounded-[28px] border border-slate-200 bg-white animate-pulse" />
            <div className="h-64 rounded-[28px] border border-slate-200 bg-white animate-pulse" />
          </div>
        ) : profile ? (
          <div className="grid gap-6 xl:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)]">
            <section className="rounded-[28px] border border-slate-200 bg-white p-8 shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
              <div className="mb-8 flex items-center justify-between gap-3">
                <div>
                  <h2 className="text-[22px] font-bold tracking-tight text-slate-900">
                    Identity
                  </h2>
                  <p className="text-[14px] font-medium text-slate-500 mt-1">
                    Data sourced from backend user service.
                  </p>
                </div>
                <button
                  onClick={loadProfile}
                  className="rounded-xl border border-slate-200 px-4 py-2 text-[14px] font-bold text-slate-700 hover:bg-slate-50 transition-all shadow-sm"
                >
                  Refresh
                </button>
              </div>

              <dl className="space-y-8">
                <div className="grid gap-2">
                  <dt className="text-[12px] font-bold uppercase tracking-widest text-slate-400">
                    User ID
                  </dt>
                  <dd className="text-[16px] font-bold text-slate-800 bg-slate-50 px-4 py-2.5 rounded-xl border border-slate-100 w-fit">
                    {profile.user_id}
                  </dd>
                </div>

                <div className="grid gap-2">
                  <dt className="text-[12px] font-bold uppercase tracking-widest text-slate-400">
                    Email Address
                  </dt>
                  <dd className="text-[16px] font-bold text-slate-800">
                    {profile.email}
                  </dd>
                </div>

                <div className="grid gap-2">
                  <dt className="text-[12px] font-bold uppercase tracking-widest text-slate-400">
                    Full Name
                  </dt>
                  <dd>
                    {isEditingName ? (
                      <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
                        <input
                          value={fullNameDraft}
                          onChange={(event) =>
                            setFullNameDraft(event.target.value)
                          }
                          className="w-full max-w-md rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-[15px] font-medium text-slate-800 focus:bg-white focus:ring-2 focus:ring-[#4338ca] transition-all focus:outline-none"
                        />
                        <div className="flex items-center gap-2">
                          <button
                            onClick={onSaveName}
                            disabled={isSaving}
                            className="rounded-xl bg-[#4338ca] px-5 py-3 text-[14px] font-bold text-white shadow-[0_10px_24px_rgba(67,56,202,0.2)] hover:bg-[#3f2fd6] transition-all disabled:opacity-50"
                          >
                            {isSaving ? "Saving..." : "Save Changes"}
                          </button>
                          <button
                            onClick={() => {
                              setIsEditingName(false);
                              setFullNameDraft(profile.full_name ?? "");
                              setError(null);
                            }}
                            className="rounded-xl border border-slate-200 px-5 py-3 text-[14px] font-bold text-slate-600 hover:bg-slate-50 transition-all shadow-sm"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-center justify-between gap-3 bg-slate-50/50 p-4 rounded-2xl border border-slate-100">
                        <span className="text-[16px] font-bold text-slate-800">
                          {profile.full_name || "No full name set"}
                        </span>
                        <button
                          onClick={() => {
                            setIsEditingName(true);
                            setSuccess(null);
                            setError(null);
                          }}
                          className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-[13px] font-bold text-[#4338ca] hover:bg-slate-50 transition-all shadow-sm"
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
              <section className="rounded-[28px] border border-slate-200 bg-white p-7 shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
                <h3 className="text-[18px] font-bold text-slate-900 mb-4">
                  Account Status
                </h3>
                <p className="inline-flex items-center gap-2 rounded-xl px-4 py-2 text-[14px] font-bold text-white bg-emerald-500 shadow-[0_8px_20px_rgba(16,185,129,0.3)]">
                  <span className="h-2 w-2 rounded-full bg-white animate-pulse" />
                  {profile.is_active ? "Active" : "Inactive"}
                </p>
                <div className="mt-8 border-t border-slate-50 pt-6">
                  <p className="text-[12px] font-bold uppercase tracking-widest text-slate-400">Last Login</p>
                  <p className="mt-2 text-[15px] font-bold text-slate-800 tracking-tight">
                    {profile.last_login
                      ? new Date(profile.last_login).toLocaleString(undefined, {
                          dateStyle: "medium",
                          timeStyle: "short",
                        })
                      : "No login history available"}
                  </p>
                </div>
              </section>

              <section className="rounded-[28px] border border-[#e0daf5] bg-[linear-gradient(180deg,#fbf9ff_0%,#f7f4ff_100%)] p-7 shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
                <h3 className="text-[18px] font-bold text-slate-900 mb-5">
                  Quick Actions
                </h3>
                <div className="space-y-3">
                  <Link
                    href="/settings"
                    className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-5 py-4 text-[14px] font-bold text-slate-700 hover:border-[#4338ca] hover:text-[#4338ca] transition-all shadow-sm group"
                  >
                    System Settings
                    <span className="opacity-0 group-hover:opacity-100 transition-opacity">→</span>
                  </Link>
                  <Link
                    href="/dashboard"
                    className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-5 py-4 text-[14px] font-bold text-slate-700 hover:border-[#4338ca] hover:text-[#4338ca] transition-all shadow-sm group"
                  >
                    Back to Dashboard
                    <span className="opacity-0 group-hover:opacity-100 transition-opacity">→</span>
                  </Link>
                </div>
              </section>
            </aside>
          </div>
        ) : (
          <div className="rounded-[28px] border border-slate-200 bg-white p-12 text-center shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
            <p className="text-[16px] font-bold text-slate-400">
              Profile data is not available.
            </p>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
