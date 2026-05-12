// Re-export dashboard icons for consistency
export {
  LogoMarkIcon as LogoIcon,
  SearchIcon,
  BellIcon,
  HelpIcon,
  SidebarToggleIcon as MenuIcon,
  DashboardGlyph as DashboardIcon,
  ProjectGlyph as ProjectIcon,
  SprintGlyph as SprintIcon,
  TasksGlyph as TasksIcon,
  AnalyticsGlyph as AnalyticsIcon,
  AIGlyph as AIIcon,
  TeamGlyph as TeamIcon,
  SettingsGlyph as SettingsIcon,
  SparkleGlyph,
} from "@/components/dashboard/icons";

// Additional icon for send button
type IconProps = {
  className?: string;
};

export function SendIcon({ className }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
      className={className}
    >
      <path
        d="M3.5 12L20 5l-7 15L10 13l-6.5-1Z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="currentColor"
      />
    </svg>
  );
}

export function CopyIcon({ className }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
      className={className}
    >
      <path
        d="M8.5 4.5h-4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-4"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M15.5 2.5h4a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2h-4a2 2 0 0 1-2-2v-4a2 2 0 0 1 2-2Z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
