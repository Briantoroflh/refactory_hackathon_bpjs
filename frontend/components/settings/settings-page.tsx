"use client";

import { useState } from "react";
import { AppLayout } from "@/components/layout/app-layout";
import type {
  SystemSettings,
  SettingsMenuItem,
  VersionControlConnection,
  GlobalSyncPolicy,
} from "@/lib/settings/types";

type SettingsPageProps = {
  settings: SystemSettings;
};

function SettingsMenu({
  menus,
  activeMenu,
  onSelectMenu,
}: {
  menus: SettingsMenuItem[];
  activeMenu: string;
  onSelectMenu: (id: string) => void;
}) {
  return (
    <div className="flex gap-1.5 border-b border-slate-200">
      {menus.map((menu) => (
        <button
          key={menu.id}
          onClick={() => onSelectMenu(menu.id)}
          className={`px-4 py-3 text-[14px] font-medium border-b-2 transition ${
            activeMenu === menu.id
              ? "border-[#4338ca] text-[#4338ca]"
              : "border-transparent text-slate-600 hover:text-slate-900"
          }`}
        >
          {menu.label}
        </button>
      ))}
    </div>
  );
}

function VersionControlCard({ vc }: { vc: VersionControlConnection }) {
  const providers = {
    github: "🐙 GitHub",
    gitlab: "🦊 GitLab",
    bitbucket: "⚙️ Bitbucket",
  };

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="flex items-start justify-between gap-4 mb-3">
        <div>
          <h4 className="text-[14px] font-semibold text-slate-900">
            {providers[vc.provider]}
          </h4>
          <p className="text-[12px] text-slate-500 mt-1">{vc.name}</p>
        </div>
        {vc.status === "connected" && (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-2.5 py-1 text-[12px] font-semibold text-emerald-700">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
            Connected
          </span>
        )}
      </div>

      <div className="flex items-center justify-between text-[13px] text-slate-600">
        <span>
          {vc.status === "connected"
            ? `Last sync: ${vc.lastSync}`
            : "Not configured"}
        </span>
        <button className="text-[#4338ca] font-medium hover:underline">
          {vc.config}
        </button>
      </div>
    </div>
  );
}

function SyncPolicyToggle({
  policy,
  onToggle,
}: {
  policy: GlobalSyncPolicy;
  onToggle: (id: string) => void;
}) {
  return (
    <div className="flex items-center justify-between rounded-lg border border-slate-200 bg-white p-4">
      <div className="flex-1">
        <h4 className="text-[14px] font-semibold text-slate-900">
          {policy.name}
        </h4>
        <p className="text-[13px] text-slate-600 mt-1">{policy.description}</p>
      </div>
      <button
        onClick={() => onToggle(policy.id)}
        className={`relative inline-flex ml-4 h-6 w-11 flex-shrink-0 items-center rounded-full transition ${
          policy.enabled ? "bg-emerald-500" : "bg-slate-300"
        }`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
            policy.enabled ? "translate-x-6" : "translate-x-1"
          }`}
        />
      </button>
    </div>
  );
}



export function SettingsPage({ settings }: SettingsPageProps) {
  const [activeMenu, setActiveMenu] = useState(
    settings.menus[0]?.id || "ia-integration",
  );
  const [syncPolicies, setSyncPolicies] = useState(settings.syncPolicies);

  const handleTogglePolicy = (policyId: string) => {
    setSyncPolicies(
      syncPolicies.map((p) =>
        p.id === policyId ? { ...p, enabled: !p.enabled } : p,
      ),
    );
  };

  return (
    <AppLayout title="System Settings" breadcrumbs={[{ label: "Configuration" }, { label: "System Settings" }]}>
      <div className="space-y-8">
        {/* Header Extra */}
        <div>
          <p className="text-[16px] font-medium text-slate-500">
            Configure platform integrations, access controls, and administrative preferences.
          </p>
        </div>

        {/* Settings Tabs */}
        <SettingsMenu
          menus={settings.menus}
          activeMenu={activeMenu}
          onSelectMenu={setActiveMenu}
        />

        <div className="grid gap-8 lg:grid-cols-[1fr_340px]">
          <div className="space-y-8">
            {/* Version Control Connections */}
            <section>
              <div className="mb-4">
                <h2 className="text-[20px] font-bold tracking-tight text-slate-900">
                  Version Control Connections
                </h2>
                <p className="text-[14px] font-medium text-slate-500 mt-1">
                  Manage external repositories linked to Bloom workspaces.
                </p>
              </div>
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {settings.versionControls.map((vc) => (
                  <VersionControlCard key={vc.id} vc={vc} />
                ))}
              </div>
            </section>

            {/* Global Sync Policies */}
            <section>
              <div className="mb-4">
                <h2 className="text-[20px] font-bold tracking-tight text-slate-900">
                  Global Sync Policies
                </h2>
                <p className="text-[14px] font-medium text-slate-500 mt-1">
                  Define how data is synchronized across the platform.
                </p>
              </div>
              <div className="space-y-3">
                {syncPolicies.map((policy) => (
                  <SyncPolicyToggle
                    key={policy.id}
                    policy={policy}
                    onToggle={handleTogglePolicy}
                  />
                ))}
              </div>
            </section>
          </div>

          {/* Sidebar Settings Info */}
          <aside className="space-y-6">
            <div className="rounded-[28px] border border-[#e0daf5] bg-[linear-gradient(180deg,#fbf9ff_0%,#f7f4ff_100%)] p-6 shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
              <h3 className="text-[18px] font-bold text-slate-900 mb-3">Sync Status</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between text-[14px]">
                  <span className="font-medium text-slate-500">Last Global Sync</span>
                  <span className="font-bold text-slate-800 text-right">2 mins ago</span>
                </div>
                <div className="flex items-center justify-between text-[14px]">
                  <span className="font-medium text-slate-500">Next Scheduled</span>
                  <span className="font-bold text-slate-800 text-right">In 28 mins</span>
                </div>
                <button className="w-full mt-2 rounded-xl bg-[#4338ca] px-4 py-3 text-[14px] font-bold text-white shadow-lg hover:bg-[#3f2fd6] transition-all">
                  Force Global Sync
                </button>
              </div>
            </div>

            <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
              <h3 className="text-[18px] font-bold text-slate-900 mb-3">API Usage</h3>
              <div className="mt-4 h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                <div className="h-full w-[65%] bg-[#4338ca] rounded-full" />
              </div>
              <p className="mt-3 text-[13px] font-medium text-slate-500">
                You have used <span className="font-bold text-slate-800">65%</span> of your monthly API quota.
              </p>
            </div>
          </aside>
        </div>
      </div>
    </AppLayout>
  );
}
