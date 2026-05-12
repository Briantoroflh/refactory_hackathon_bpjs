"use client";

import { useMemo, useState } from "react";
import { findProjectById, projectsMockData } from "@/lib/projects/mock-data";
import { filterAndSortProjects } from "@/lib/projects/selectors";
import type { ProjectFilterState } from "@/lib/projects/types";
import { ProjectCard } from "./project-card";
import { ProjectDetailModal } from "./project-detail-modal";
import { ProjectsEmptyState } from "./projects-empty-state";
import { ProjectsFilters } from "./projects-filters";
import { ProjectsNavbar } from "./projects-navbar";
import { ProjectsSidebar } from "./projects-sidebar";
import { RepositoriesTable } from "./repositories-table";

const defaultFilters: ProjectFilterState = {
  query: "",
  platform: "all",
  status: "all",
  sortBy: "updated",
  view: "grid",
};

export function ProjectsPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [filters, setFilters] = useState<ProjectFilterState>(defaultFilters);
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);

  const visibleProjects = useMemo(
    () =>
      filterAndSortProjects(projectsMockData.projects, {
        query: filters.query,
        platform: filters.platform,
        status: filters.status,
        sortBy: filters.sortBy,
      }),
    [filters],
  );

  const selectedProject = useMemo(
    () =>
      selectedProjectId
        ? findProjectById(projectsMockData.projects, selectedProjectId)
        : undefined,
    [selectedProjectId],
  );

  return (
    <div className="min-h-screen bg-[#eef1f8] text-slate-900">
      <div className="mx-auto flex min-h-screen w-full overflow-hidden bg-white xl:my-4 xl:rounded-[24px] xl:border xl:border-slate-200 xl:shadow-[0_10px_40px_rgba(15,23,42,0.08)]">
        <ProjectsSidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <div className="flex min-w-0 flex-1 flex-col">
          <ProjectsNavbar
            query={filters.query}
            onQueryChange={(query) => setFilters((current) => ({ ...current, query }))}
            onOpenSidebar={() => setSidebarOpen(true)}
          />

          <main className="flex-1 overflow-y-auto bg-[#f8f9fd] px-4 py-5 sm:px-6 lg:px-8">
            <section>
              <h1 className="text-[36px] font-semibold tracking-[-0.04em] text-slate-800 sm:text-[40px] lg:text-[52px]">
                Active Projects
              </h1>
              <p className="mt-2 text-[17px] text-slate-600 sm:text-[18px] lg:text-[30px]">
                Manage and monitor repository health and engineering velocity.
              </p>
            </section>

            <div className="mt-5">
              <ProjectsFilters filters={filters} onFiltersChange={setFilters} />
            </div>
            <div className="mt-4 hidden items-center gap-3 md:flex">
              <select
                value={filters.platform}
                onChange={(event) =>
                  setFilters((current) => ({
                    ...current,
                    platform: event.target.value as ProjectFilterState["platform"],
                  }))
                }
                className="h-10 rounded-xl border border-slate-200 bg-white px-3 text-[14px] text-slate-700"
              >
                <option value="all">All platforms</option>
                <option value="GitHub">GitHub</option>
                <option value="GitLab">GitLab</option>
              </select>
              <select
                value={filters.status}
                onChange={(event) =>
                  setFilters((current) => ({
                    ...current,
                    status: event.target.value as ProjectFilterState["status"],
                  }))
                }
                className="h-10 rounded-xl border border-slate-200 bg-white px-3 text-[14px] text-slate-700"
              >
                <option value="all">All status</option>
                <option value="healthy">Healthy</option>
                <option value="warning">Warning</option>
                <option value="critical">Critical</option>
              </select>
              <select
                value={filters.sortBy}
                onChange={(event) =>
                  setFilters((current) => ({
                    ...current,
                    sortBy: event.target.value as ProjectFilterState["sortBy"],
                  }))
                }
                className="h-10 rounded-xl border border-slate-200 bg-white px-3 text-[14px] text-slate-700"
              >
                <option value="updated">Latest update</option>
                <option value="health-desc">Health high to low</option>
                <option value="health-asc">Health low to high</option>
                <option value="velocity-desc">Velocity high to low</option>
              </select>
              <div className="ml-auto inline-flex rounded-xl border border-slate-200 bg-white p-1">
                <button
                  type="button"
                  onClick={() =>
                    setFilters((current) => ({
                      ...current,
                      view: "grid",
                    }))
                  }
                  className={`rounded-lg px-3 py-1 text-sm font-semibold ${
                    filters.view === "grid" ? "bg-[#4338ca] text-white" : "text-slate-600"
                  }`}
                >
                  Grid
                </button>
                <button
                  type="button"
                  onClick={() =>
                    setFilters((current) => ({
                      ...current,
                      view: "list",
                    }))
                  }
                  className={`rounded-lg px-3 py-1 text-sm font-semibold ${
                    filters.view === "list" ? "bg-[#4338ca] text-white" : "text-slate-600"
                  }`}
                >
                  List
                </button>
              </div>
            </div>

            <section className="mt-6 space-y-6">
              {visibleProjects.length ? (
                <div
                  className={
                    filters.view === "grid"
                      ? "grid gap-5 md:grid-cols-2 2xl:grid-cols-3"
                      : "space-y-4"
                  }
                >
                  {visibleProjects.map((project) => (
                    <ProjectCard
                      key={project.id}
                      project={project}
                      onOpenDetail={(projectId) => setSelectedProjectId(projectId)}
                    />
                  ))}
                </div>
              ) : (
                <ProjectsEmptyState
                  title="No projects found"
                  description="Try a different search or filter. Once your FastAPI backend is connected, live projects will appear here."
                />
              )}

              {projectsMockData.repositories.length ? (
                <RepositoriesTable repositories={projectsMockData.repositories} />
              ) : (
                <ProjectsEmptyState
                  title="No connected repositories"
                  description="Connect your GitHub or GitLab repositories to start monitoring project health."
                />
              )}
            </section>
          </main>
        </div>
      </div>

      {selectedProject ? (
        <ProjectDetailModal
          project={selectedProject}
          onClose={() => setSelectedProjectId(null)}
        />
      ) : null}
    </div>
  );
}
