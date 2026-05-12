"use client";

import { useMemo, useState } from "react";
import { findProjectById, projectsMockData } from "@/lib/projects/mock-data";
import { filterAndSortProjects } from "@/lib/projects/selectors";
import type { ProjectFilterState } from "@/lib/projects/types";
import { ProjectCard } from "./project-card";
import { ProjectDetailModal } from "./project-detail-modal";
import { ProjectsEmptyState } from "./projects-empty-state";
import { ProjectsFilters } from "./projects-filters";
import { RepositoriesTable } from "./repositories-table";
import { AppLayout } from "@/components/layout/app-layout";

const defaultFilters: ProjectFilterState = {
  query: "",
  platform: "all",
  status: "all",
  sortBy: "updated",
  view: "grid",
};

export function ProjectsPage() {
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
    <AppLayout title="Active Projects">
      <div className="space-y-6">
        <section>
          <p className="text-[16px] text-slate-600 sm:text-[17px]">
            Manage and monitor repository health and engineering velocity.
          </p>
        </section>

        <div className="flex flex-col gap-4">
          <ProjectsFilters filters={filters} onFiltersChange={setFilters} />
          
          <div className="flex items-center gap-3 flex-wrap">
            <select
              value={filters.platform}
              onChange={(event) =>
                setFilters((current) => ({
                  ...current,
                  platform: event.target.value as ProjectFilterState["platform"],
                }))
              }
              className="h-11 rounded-2xl border border-slate-200 bg-white px-4 text-[14px] text-slate-700 font-medium shadow-sm"
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
              className="h-11 rounded-2xl border border-slate-200 bg-white px-4 text-[14px] text-slate-700 font-medium shadow-sm"
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
              className="h-11 rounded-2xl border border-slate-200 bg-white px-4 text-[14px] text-slate-700 font-medium shadow-sm"
            >
              <option value="updated">Latest update</option>
              <option value="health-desc">Health high to low</option>
              <option value="health-asc">Health low to high</option>
              <option value="velocity-desc">Velocity high to low</option>
            </select>
            
            <div className="ml-auto inline-flex rounded-2xl border border-slate-200 bg-white p-1 shadow-sm">
              <button
                type="button"
                onClick={() =>
                  setFilters((current) => ({
                    ...current,
                    view: "grid",
                  }))
                }
                className={`rounded-xl px-4 py-1.5 text-sm font-bold transition-all ${
                  filters.view === "grid" ? "bg-[#4338ca] text-white shadow-[0_8px_16px_rgba(67,56,202,0.2)]" : "text-slate-600 hover:text-slate-900"
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
                className={`rounded-xl px-4 py-1.5 text-sm font-bold transition-all ${
                  filters.view === "list" ? "bg-[#4338ca] text-white shadow-[0_8px_16px_rgba(67,56,202,0.2)]" : "text-slate-600 hover:text-slate-900"
                }`}
              >
                List
              </button>
            </div>
          </div>
        </div>

        <section className="space-y-8">
          {visibleProjects.length ? (
            <div
              className={
                filters.view === "grid"
                  ? "grid gap-6 md:grid-cols-2 2xl:grid-cols-3"
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

          <div className="pt-4">
            <h2 className="text-[22px] font-bold tracking-tight text-slate-800 mb-4">Connected Repositories</h2>
            {projectsMockData.repositories.length ? (
              <RepositoriesTable repositories={projectsMockData.repositories} />
            ) : (
              <ProjectsEmptyState
                title="No connected repositories"
                description="Connect your GitHub or GitLab repositories to start monitoring project health."
              />
            )}
          </div>
        </section>

        {selectedProject ? (
          <ProjectDetailModal
            project={selectedProject}
            onClose={() => setSelectedProjectId(null)}
          />
        ) : null}
      </div>
    </AppLayout>
  );
}
