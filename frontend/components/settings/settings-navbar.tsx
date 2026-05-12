"use client";

import {
  BellIcon,
  HelpIcon,
  SidebarToggleIcon,
  SearchIcon,
} from "@/components/dashboard/icons";

type SettingsNavbarProps = {
  query: string;
  onOpenSidebar: () => void;
  onQueryChange: (value: string) => void;
};

export function SettingsNavbar({
  query,
  onOpenSidebar,
  onQueryChange,
}: SettingsNavbarProps) {
  return (
    <header className="flex h-[82px] items-center gap-4 border-b border-slate-200 bg-white px-4 sm:px-6 lg:px-8">
      <button
        type="button"
        onClick={onOpenSidebar}
        className="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 text-slate-600 lg:hidden"
        aria-label="Open sidebar"
      >
        <SidebarToggleIcon className="h-5 w-5" />
      </button>

      <div className="hidden items-center gap-2 text-[15px] font-semibold text-slate-500 md:flex">
        <span>Settings</span>
        <span className="text-slate-300">›</span>
        <span className="text-[#3f2fd6]">System Settings</span>
      </div>

      <div className="ml-auto flex w-full max-w-[320px] items-center rounded-full border border-[#e5def7] bg-[#f3ecfc] px-4 py-2.5 text-slate-400">
        <SearchIcon className="h-5 w-5 shrink-0" />
        <input
          aria-label="Search settings"
          placeholder="Search settings..."
          value={query}
          onChange={(event) => onQueryChange(event.target.value)}
          className="ml-3 w-full border-0 bg-transparent text-[15px] text-slate-700 placeholder:text-slate-400 focus:outline-none"
        />
      </div>

      <div className="hidden items-center gap-3 sm:flex">
        <button
          className="inline-flex h-11 w-11 items-center justify-center rounded-full text-slate-500 hover:bg-slate-100"
          aria-label="Notifications"
        >
          <BellIcon className="h-5 w-5" />
        </button>
        <button
          className="inline-flex h-11 w-11 items-center justify-center rounded-full text-slate-500 hover:bg-slate-100"
          aria-label="Help"
        >
          <HelpIcon className="h-5 w-5" />
        </button>
      </div>

      <button
        className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-slate-200 text-[12px] font-bold text-slate-600"
        aria-label="User profile"
      >
        MC
      </button>
    </header>
  );
}
