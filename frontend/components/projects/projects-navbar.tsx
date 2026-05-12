"use client";

import { BellIcon, HelpIcon, MenuIcon, PlusIcon, SearchIcon } from "./project-icons";

type ProjectsNavbarProps = {
  query: string;
  onQueryChange: (value: string) => void;
  onOpenSidebar: () => void;
};

export function ProjectsNavbar({
  query,
  onQueryChange,
  onOpenSidebar,
}: ProjectsNavbarProps) {
  return (
    <header className="flex h-[84px] items-center gap-4 border-b border-slate-200 bg-white px-4 sm:px-6 lg:px-8">
      <button
        type="button"
        onClick={onOpenSidebar}
        className="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 text-slate-600 lg:hidden"
        aria-label="Open sidebar"
      >
        <MenuIcon className="h-5 w-5" />
      </button>

      <div className="hidden min-w-0 flex-1 items-center rounded-2xl border border-[#e5def7] bg-[#f4eefc] px-4 py-3 text-slate-400 shadow-[0_1px_0_rgba(15,23,42,0.02)] md:flex md:max-w-[420px]">
        <SearchIcon className="h-5 w-5 shrink-0" />
        <input
          aria-label="Search projects"
          placeholder="Search projects..."
          value={query}
          onChange={(event) => onQueryChange(event.target.value)}
          className="ml-3 w-full border-0 bg-transparent text-[15px] text-slate-700 placeholder:text-slate-400 focus:outline-none"
        />
      </div>

      <button className="inline-flex h-11 items-center gap-2 rounded-xl bg-[#3f2fd6] px-4 text-[15px] font-semibold text-white shadow-[0_10px_24px_rgba(63,47,214,0.24)]">
        <PlusIcon className="h-5 w-5" />
        <span>New Project</span>
      </button>

      <div className="ml-auto flex items-center gap-3">
        <button className="hidden h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 text-slate-600 sm:inline-flex" aria-label="Notifications">
          <BellIcon className="h-5 w-5" />
        </button>
        <button className="hidden h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 text-slate-600 sm:inline-flex" aria-label="Help">
          <HelpIcon className="h-5 w-5" />
        </button>
        <div className="h-11 w-11 rounded-full bg-[radial-gradient(circle_at_30%_30%,#d1a36d,#4b2f1f)] shadow-[0_8px_18px_rgba(15,23,42,0.2)]" />
      </div>
    </header>
  );
}
