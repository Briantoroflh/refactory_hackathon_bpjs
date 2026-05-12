type IconProps = {
  className?: string;
};

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

export function MenuIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

export function PlusIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

export function RepoIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <rect x="4" y="4" width="16" height="16" rx="3" stroke="currentColor" strokeWidth="1.7" />
      <path d="M8 9h8M8 12h8M8 15h5" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
    </svg>
  );
}

export function DotsIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <circle cx="12" cy="5" r="1.8" fill="currentColor" />
      <circle cx="12" cy="12" r="1.8" fill="currentColor" />
      <circle cx="12" cy="19" r="1.8" fill="currentColor" />
    </svg>
  );
}

export function DashboardIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <rect x="4.5" y="4.5" width="6.5" height="6.5" stroke="currentColor" strokeWidth="1.7" />
      <rect x="13" y="4.5" width="6.5" height="6.5" stroke="currentColor" strokeWidth="1.7" />
      <rect x="4.5" y="13" width="6.5" height="6.5" stroke="currentColor" strokeWidth="1.7" />
      <rect x="13" y="13" width="6.5" height="6.5" stroke="currentColor" strokeWidth="1.7" />
    </svg>
  );
}

export function ProjectIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <rect x="4" y="5" width="16" height="14" rx="2.5" stroke="currentColor" strokeWidth="1.7" />
      <path d="M4 9h16" stroke="currentColor" strokeWidth="1.7" />
    </svg>
  );
}

export function SprintIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <path d="M5 16c1.5-4 3.5-6 7-6s5.5 2 7-2" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <path d="m16.5 6.5 2.5 1-1 2.5" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M5 19h14" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
    </svg>
  );
}

export function TasksIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <path d="M8.5 12.5 11 15l4.5-5" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
      <rect x="4.5" y="4.5" width="15" height="15" rx="4" stroke="currentColor" strokeWidth="1.7" />
    </svg>
  );
}

export function AnalyticsIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <path d="M4.5 19.5h15" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <rect x="6" y="12" width="2.8" height="6.5" rx="1" stroke="currentColor" strokeWidth="1.7" />
      <rect x="10.6" y="9" width="2.8" height="9.5" rx="1" stroke="currentColor" strokeWidth="1.7" />
      <rect x="15.2" y="6.5" width="2.8" height="12" rx="1" stroke="currentColor" strokeWidth="1.7" />
    </svg>
  );
}

export function AIIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <path d="M12 3.5v3M12 17.5v3M4.5 12h3M16.5 12h3" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <path d="m7 7 2 2m6-2-2 2m-6 6 2-2m6 2-2-2" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <circle cx="12" cy="12" r="3.5" stroke="currentColor" strokeWidth="1.7" />
    </svg>
  );
}

export function TeamIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" className={className}>
      <circle cx="8" cy="9" r="2.5" stroke="currentColor" strokeWidth="1.7" />
      <circle cx="16" cy="10.5" r="2.2" stroke="currentColor" strokeWidth="1.7" />
      <path d="M4.8 18.5a4.2 4.2 0 0 1 6.4-3.5" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <path d="M12.5 18.5a4.3 4.3 0 0 1 6.2-3.4" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
    </svg>
  );
}

export function SettingsIcon({ className }: IconProps) {
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

