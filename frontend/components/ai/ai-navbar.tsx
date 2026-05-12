"use client";

import { BellIcon, HelpIcon, MenuIcon, SearchIcon } from "./ai-icons";

type AINavbarProps = {
  onMenuClick: () => void;
};

export function AINavbar({ onMenuClick }: AINavbarProps) {
  return (
    <header className="flex h-[84px] items-center gap-4 border-b border-slate-200 bg-white px-4 sm:px-6 lg:px-8">
      <button
        type="button"
        onClick={onMenuClick}
        className="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 text-slate-600 lg:hidden"
        aria-label="Open sidebar"
      >
        <MenuIcon className="h-5 w-5" />
      </button>
      <div className="min-w-0 flex-1">
        <h1 className="truncate text-[26px] font-semibold tracking-[-0.03em] text-slate-800 sm:text-[32px]">
          AI Assistant
        </h1>
      </div>
      <div className="hidden w-full max-w-[clamp(220px,24vw,360px)] flex-1 items-center rounded-2xl border border-[#e5def7] bg-[#f4eefc] px-4 py-3 text-slate-400 shadow-[0_1px_0_rgba(15,23,42,0.02)] lg:flex">
        <SearchIcon className="h-5 w-5 shrink-0" />
        <input
          aria-label="Search"
          placeholder="Search issues, code..."
          className="ml-3 w-full border-0 bg-transparent text-[15px] text-slate-700 placeholder:text-slate-400 focus:outline-none"
        />
      </div>
      <button
        className="hidden h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 text-slate-600 sm:inline-flex"
        aria-label="Notifications"
      >
        <BellIcon className="h-5 w-5" />
      </button>
      <button
        className="hidden h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 text-slate-600 sm:inline-flex"
        aria-label="Help"
      >
        <HelpIcon className="h-5 w-5" />
      </button>
      <div className="h-11 w-11 rounded-full bg-[radial-gradient(circle_at_30%_30%,#374151,#0f172a)] shadow-[0_8px_18px_rgba(15,23,42,0.2)]" />
    </header>
  );
}
