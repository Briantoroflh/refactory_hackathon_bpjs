import type { ProjectFilterState } from "@/lib/projects/types";
import { SearchIcon } from "./project-icons";

type ProjectsFiltersProps = {
  filters: ProjectFilterState;
  onFiltersChange: (next: ProjectFilterState) => void;
};

export function ProjectsFilters({ filters, onFiltersChange }: ProjectsFiltersProps) {
  return (
    <section className="space-y-3 rounded-[20px] border border-slate-200 bg-white p-4 shadow-[0_8px_20px_rgba(15,23,42,0.04)] md:hidden">
      <div className="flex items-center rounded-xl border border-[#e5def7] bg-[#f4eefc] px-3 py-3 text-slate-400">
        <SearchIcon className="h-5 w-5 shrink-0" />
        <input
          placeholder="Search projects..."
          value={filters.query}
          onChange={(event) =>
            onFiltersChange({
              ...filters,
              query: event.target.value,
            })
          }
          className="ml-2 w-full border-0 bg-transparent text-[14px] text-slate-700 placeholder:text-slate-400 focus:outline-none"
        />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <select
          value={filters.platform}
          onChange={(event) =>
            onFiltersChange({
              ...filters,
              platform: event.target.value as ProjectFilterState["platform"],
            })
          }
          className="h-10 rounded-xl border border-slate-200 bg-white px-3 text-[14px] text-slate-700"
        >
          <option value="all">All platforms</option>
          <option value="GitHub">GitHub</option>
          <option value="GitLab">GitLab</option>
        </select>

        <select
          value={filters.sortBy}
          onChange={(event) =>
            onFiltersChange({
              ...filters,
              sortBy: event.target.value as ProjectFilterState["sortBy"],
            })
          }
          className="h-10 rounded-xl border border-slate-200 bg-white px-3 text-[14px] text-slate-700"
        >
          <option value="updated">Latest update</option>
          <option value="health-desc">Health high to low</option>
          <option value="health-asc">Health low to high</option>
          <option value="velocity-desc">Velocity high to low</option>
        </select>
      </div>
    </section>
  );
}

