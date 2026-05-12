"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { filterAndSortProjects } from "@/lib/projects/selectors";
import { fetchProjectsPageData } from "@/lib/projects/api";
import type { ProjectFilterState, ProjectsPageData } from "@/lib/projects/types";
import { ProjectCard } from "./project-card";
import { ProjectDetailModal } from "./project-detail-modal";
import { ProjectsEmptyState } from "./projects-empty-state";
import { ProjectsFilters } from "./projects-filters";
import { RepositoriesTable } from "./repositories-table";
import { AppLayout } from "@/components/layout/app-layout";
import { ProjectsSkeleton } from "./projects-skeleton";

const defaultFilters: ProjectFilterState = {
  query: "",
  platform: "all",
  status: "all",
  sortBy: "updated",
  view: "grid",
};

const emptyProjectsPageData: ProjectsPageData = {
  projects: [],
  repositories: [],
};

export function ProjectsPage() {
  const [filters, setFilters] = useState<ProjectFilterState>(defaultFilters);
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [pageData, setPageData] = useState<ProjectsPageData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadPageData = useCallback(async () => {
    try {
      const data = await fetchProjectsPageData();
      setPageData({
        projects: data.projects ?? [],
        repositories: data.repositories ?? [],
      });
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load projects");
    }
  }, []);

  useEffect(() => {
    let active = true;

    const run = async () => {
      try {
        const data = await fetchProjectsPageData();
        if (!active) return;
        setPageData({
          projects: data.projects ?? [],
          repositories: data.repositories ?? [],
        });
        setError(null);
      } catch (err) {
        if (!active) return;
        setError(err instanceof Error ? err.message : "Failed to load projects");
      }
    };

    run();
    const timer = window.setInterval(run, 30000);

    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, []);

  const data = pageData ?? emptyProjectsPageData;

  const visibleProjects = useMemo(
    () =>
      filterAndSortProjects(data.projects, {
        query: filters.query,
        platform: filters.platform,
        status: filters.status,
        sortBy: filters.sortBy,
      }),
    [data.projects, filters],
  );

  const selectedProject = useMemo(
    () => (selectedProjectId ? data.projects.find((project) => project.id === selectedProjectId) : undefined),
    [data.projects, selectedProjectId],
  );

  useEffect(() => {
    if (selectedProjectId && !selectedProject) {
      setSelectedProjectId(null);
    }
  }, [selectedProject, selectedProjectId]);

  if (!pageData && !error) {
    return <ProjectsSkeleton />;
  }

  if (!pageData && error) {
    return (
      <AppLayout title="Active Projects">
        <div className="rounded-[24px] border border-rose-200 bg-white p-6 text-slate-700 shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
          <p className="text-[18px] font-semibold text-slate-800">Gagal memuat projects</p>
          <p className="mt-2 text-[14px] leading-6 text-slate-500">{error}</p>
          <button
            type="button"
            onClick={loadPageData}
            className="mt-5 rounded-2xl bg-[#3f2fd6] px-4 py-3 text-[14px] font-semibold text-white"
          >
            Coba lagi
          </button>
        </div>
      </AppLayout>
    );
  }

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
            {data.repositories.length ? (
              <RepositoriesTable repositories={data.repositories} />
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
