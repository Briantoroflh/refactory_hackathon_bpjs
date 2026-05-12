import type { SystemSettings } from "./types";

export const mockSystemSettings: SystemSettings = {
  menus: [
    {
      id: "ia-integration",
      label: "IA Integration",
      description: "Configure AI model integrations, access controls",
    },
    {
      id: "team-access",
      label: "Team Access Control",
      description: "Manage member roles, permissions, and security policies",
    },
    {
      id: "ai-settings",
      label: "AI Assistant Settings",
      description: "Configure AI assistant behavior and model preferences",
    },
  ],
  versionControls: [
    {
      id: "vc-1",
      name: "GitHub Enterprise",
      provider: "github",
      status: "connected",
      lastSync: "2 mins ago",
      config: "28 configure",
    },
    {
      id: "vc-2",
      name: "GitLab",
      provider: "gitlab",
      status: "not-configured",
      config: "Configure",
    },
    {
      id: "vc-3",
      name: "Bitbucket",
      provider: "bitbucket",
      status: "not-configured",
      config: "Configure",
    },
  ],
  syncPolicies: [
    {
      id: "policy-1",
      name: "Auto Sync Enabled",
      description: "Automatically create Bloom tasks when a PR is created.",
      enabled: true,
    },
    {
      id: "policy-2",
      name: "Require Status Checks",
      description: "Block PR merge completion until CI/CD checks pass in GH.",
      enabled: false,
    },
  ],
};
