import { SettingsPage } from "@/components/settings/settings-page";
import { mockSystemSettings } from "@/lib/settings/mock-data";

export default function Page() {
  return <SettingsPage settings={mockSystemSettings} />;
}
