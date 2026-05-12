import { TeamPage } from "@/components/team/team-page";
import { mockTeamAccessControl } from "@/lib/team/mock-data";

export default function Page() {
  return <TeamPage accessControl={mockTeamAccessControl} />;
}
