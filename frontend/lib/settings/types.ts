export interface SettingsMenuItem {
  id: string;
  label: string;
  description?: string;
  icon?: string;
}

export interface VersionControlConnection {
  id: string;
  name: string;
  provider: "github" | "gitlab" | "bitbucket";
  status: "connected" | "not-configured";
  lastSync?: string;
  config?: string;
}

export interface GlobalSyncPolicy {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
}

export interface SystemSettings {
  menus: SettingsMenuItem[];
  versionControls: VersionControlConnection[];
  syncPolicies: GlobalSyncPolicy[];
}
