"use client";

import { useState } from "react";
import { SettingsNavbar } from "./settings-navbar";
import { SettingsSidebar } from "./settings-sidebar";
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
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [query, setQuery] = useState("");
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
    <div className="flex h-screen bg-slate-50">
      <SettingsSidebar
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <div className="flex flex-1 flex-col overflow-hidden">
        <SettingsNavbar
          query={query}
          onOpenSidebar={() => setSidebarOpen(true)}
          onQueryChange={setQuery}
        />

        <main className="flex-1 overflow-y-auto">
          <div className="space-y-6 p-4 sm:p-6 lg:p-8">
            {/* Header */}
            <div>
              <h1 className="text-[28px] font-bold text-slate-900">
                System Settings
              </h1>
              <p className="mt-1 text-[15px] text-slate-600">
                Configure platform integrations, access controls, and
                administrative preferences.
              </p>
            </div>

            {/* Settings Tabs */}
            <SettingsMenu
              menus={settings.menus}
              activeMenu={activeMenu}
              onSelectMenu={setActiveMenu}
            />

            {/* Version Control Connections */}
            <div>
              <h2 className="text-[18px] font-semibold text-slate-900 mb-4">
                Version Control Connections
              </h2>
              <p className="text-[14px] text-slate-600 mb-4">
                Manage external repositories linked to Bloom workspaces.
              </p>
              <div className="grid gap-3 md:grid-cols-3">
                {settings.versionControls.map((vc) => (
                  <VersionControlCard key={vc.id} vc={vc} />
                ))}
              </div>
            </div>

            {/* Global Sync Policies */}
            <div>
              <h2 className="text-[18px] font-semibold text-slate-900 mb-4">
                Global Sync Policies
              </h2>
              <div className="space-y-3 max-w-2xl">
                {syncPolicies.map((policy) => (
                  <SyncPolicyToggle
                    key={policy.id}
                    policy={policy}
                    onToggle={handleTogglePolicy}
                  />
                ))}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
