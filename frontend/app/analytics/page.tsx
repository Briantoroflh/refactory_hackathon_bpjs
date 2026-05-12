import { AnalyticsPage } from "@/components/analytics/analytics-page";
import { mockTeamAnalytics } from "@/lib/analytics/mock-data";

export default function Page() {
  return <AnalyticsPage analytics={mockTeamAnalytics} />;
}
