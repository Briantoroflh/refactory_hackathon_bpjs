type IconProps = {
  className?: string;
};

export function LogoMarkIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 36 36" fill="none" aria-hidden="true" className={className}>
      <rect x="2" y="2" width="32" height="32" rx="10" fill="#4f46e5" />
      <path
        d="M18 8c-3.8 5-8.8 8.9-8.8 15.1C9.2 28.3 13.1 31 18 31s8.8-2.7 8.8-7.9C26.8 16.9 21.8 13 18 8Z"
        stroke="white"
        strokeWidth="2.4"
        strokeLinejoin="round"
      />
      <circle cx="18" cy="19" r="3.3" stroke="white" strokeWidth="2.4" />
    </svg>
  );
}

export function SearchIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <circle cx="11" cy="11" r="6.5" stroke="currentColor" strokeWidth="1.8" />
      <path d="m16 16 4.5 4.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

export function BellIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <path
        d="M12 4.5a4.8 4.8 0 0 0-4.8 4.8v2.1c0 .8-.2 1.6-.7 2.3l-1 1.5h13l-1-1.5a4.3 4.3 0 0 1-.7-2.3V9.3A4.8 4.8 0 0 0 12 4.5Z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
      />
      <path d="M9.5 18a2.5 2.5 0 0 0 5 0" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
    </svg>
  );
}

export function HelpIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.7" />
      <path d="M9.8 9.5a2.4 2.4 0 1 1 3.8 2c-.8.5-1.6 1.1-1.6 2.5" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <circle cx="12" cy="17" r="1" fill="currentColor" />
    </svg>
  );
}

export function SidebarToggleIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

export function DashboardGlyph({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <rect x="4" y="4" width="16" height="16" rx="4" stroke="currentColor" strokeWidth="1.7" />
      <path d="M7 15h3V9H7v6Zm5 0h3V6h-3v9Zm5 0h0" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" />
    </svg>
  );
}

export function ProjectGlyph({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <path d="M4.5 7.5h15v11h-15z" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" />
      <path d="M4.5 10.5h15M8 7.5v11" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
    </svg>
  );
}

export function SprintGlyph({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <path d="M5 16c1.5-4 3.5-6 7-6s5.5 2 7-2" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <path d="m16.5 6.5 2.5 1-1 2.5" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M5 19h14" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
    </svg>
  );
}

export function TasksGlyph({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <path d="M8.5 12.5 11 15l4.5-5" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
      <rect x="4.5" y="4.5" width="15" height="15" rx="4" stroke="currentColor" strokeWidth="1.7" />
    </svg>
  );
}

export function AnalyticsGlyph({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <path d="M4.5 19.5h15" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <rect x="6" y="12" width="2.8" height="6.5" rx="1" stroke="currentColor" strokeWidth="1.7" />
      <rect x="10.6" y="9" width="2.8" height="9.5" rx="1" stroke="currentColor" strokeWidth="1.7" />
      <rect x="15.2" y="6.5" width="2.8" height="12" rx="1" stroke="currentColor" strokeWidth="1.7" />
    </svg>
  );
}

export function AIGlyph({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <path d="M12 3.5v3M12 17.5v3M4.5 12h3M16.5 12h3" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <path d="m7 7 2 2m6-2-2 2m-6 6 2-2m6 2-2-2" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <circle cx="12" cy="12" r="3.5" stroke="currentColor" strokeWidth="1.7" />
    </svg>
  );
}

export function TeamGlyph({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <circle cx="8" cy="9" r="2.5" stroke="currentColor" strokeWidth="1.7" />
      <circle cx="16" cy="10.5" r="2.2" stroke="currentColor" strokeWidth="1.7" />
      <path d="M4.8 18.5a4.2 4.2 0 0 1 6.4-3.5" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <path d="M12.5 18.5a4.3 4.3 0 0 1 6.2-3.4" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
    </svg>
  );
}

export function SettingsGlyph({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <path
        d="m12 5.5 1.2 2.1 2.4.4-.5 2.3 1.8 1.6-1.8 1.6.5 2.3-2.4.4L12 18.5l-1.2-2.1-2.4-.4.5-2.3-1.8-1.6 1.8-1.6-.5-2.3 2.4-.4L12 5.5Z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
      <circle cx="12" cy="12" r="2.4" stroke="currentColor" strokeWidth="1.6" />
    </svg>
  );
}

export function TrendGlyph({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <path d="M5 16.5 10 11l3.2 3.2L19 8.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      <path d="m16.5 8.5 2.5.2-.2 2.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function CheckGlyph({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <circle cx="12" cy="12" r="8.5" stroke="currentColor" strokeWidth="1.8" />
      <path d="m8.5 12.5 2.3 2.3 4.7-5.2" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function FlameGlyph({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <path
        d="M12 3.5c1.1 2.8-.8 4.7-2.1 6.4C8.3 11.4 8 12.7 8 14a4 4 0 1 0 8 0c0-1.7-.7-3.2-1.7-4.4-.8-.9-1.2-1.8-1.3-3 .9.7 2.8 2.4 2.8 5.4"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function BlockGlyph({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <circle cx="12" cy="12" r="8.5" stroke="currentColor" strokeWidth="1.8" />
      <path d="M8.5 8.5 15.5 15.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

export function SparkleGlyph({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <path d="m12 3 1.2 4.1L17 8.3l-3.8 1.2L12 13.6l-1.2-4.1L7 8.3l3.8-1.2L12 3Z" fill="currentColor" />
      <path d="m18 13 0.7 2.4 2.3.7-2.3.7L18 19.2l-.7-2.4-2.3-.7 2.3-.7L18 13Z" fill="currentColor" />
    </svg>
  );
}

