"use client";

import { BellIcon, HelpIcon, MenuIcon, SearchIcon } from "./sprint-icons";

type SprintNavbarProps = {
  query: string;
  breadcrumbs: string[];
  onOpenSidebar: () => void;
  onQueryChange: (value: string) => void;
};

export function SprintNavbar({
  query,
  breadcrumbs,
  onOpenSidebar,
  onQueryChange,
}: SprintNavbarProps) {
  return (
    <header className="flex h-[82px] items-center gap-4 border-b border-slate-200 bg-white px-4 sm:px-6 lg:px-8">
      <button
        type="button"
        onClick={onOpenSidebar}
        className="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 text-slate-600 lg:hidden"
        aria-label="Open sidebar"
      >
        <MenuIcon className="h-5 w-5" />
      </button>

      <div className="hidden items-center gap-2 text-[15px] font-semibold text-slate-500 md:flex">
        {breadcrumbs.map((crumb, index) => (
          <span key={crumb} className="inline-flex items-center gap-2">
            {index ? <span className="text-slate-300">›</span> : null}
            <span className={index === breadcrumbs.length - 1 ? "text-[#3f2fd6]" : ""}>{crumb}</span>
          </span>
        ))}
      </div>

      <div className="ml-auto flex w-full max-w-[320px] items-center rounded-full border border-[#e5def7] bg-[#f3ecfc] px-4 py-2.5 text-slate-400">
        <SearchIcon className="h-5 w-5 shrink-0" />
        <input
          aria-label="Search sprint tasks"
          placeholder="Search issues, code..."
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
        <div className="inline-flex h-11 w-11 items-center justify-center rounded-full bg-[#2563eb] text-sm font-bold text-white">
          JD
        </div>
      </div>
    </header>
  );
}

