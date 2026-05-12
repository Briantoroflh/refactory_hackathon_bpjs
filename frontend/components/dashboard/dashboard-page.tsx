import { DashboardShell } from "./dashboard-shell";
import { dashboardOverview } from "@/lib/dashboard/mock-data";

export function DashboardPage() {
  return <DashboardShell overview={dashboardOverview} />;
}
