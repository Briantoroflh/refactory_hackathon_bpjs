"use client";

import type { ProjectItem } from "@/lib/projects/types";
import { ProjectProgress } from "./project-progress";
import { ProjectStatusBadge } from "./project-status-badge";

type ProjectDetailModalProps = {
  project: ProjectItem;
  onClose: () => void;
};

export function ProjectDetailModal({ project, onClose }: ProjectDetailModalProps) {
  return (
    <div className="fixed inset-0 z-[70] flex items-center justify-center bg-slate-950/40 p-4">
      <div className="w-full max-w-[640px] rounded-[24px] border border-slate-200 bg-white p-6 shadow-[0_24px_48px_rgba(15,23,42,0.22)]">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-[30px] font-semibold tracking-[-0.03em] text-slate-900">
              {project.name}
            </h2>
            <p className="text-[15px] text-slate-500">{project.platform}</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-xl border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-600"
          >
            Close
          </button>
        </div>

        <p className="mt-4 text-[15px] leading-7 text-slate-600">{project.description}</p>

        <div className="mt-5 grid gap-4 sm:grid-cols-2">
          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-xs uppercase tracking-[0.14em] text-slate-500">AI Health Score</p>
            <div className="mt-2 flex items-center gap-2">
              <p className="text-[34px] font-semibold tracking-[-0.03em] text-slate-900">
                {project.aiHealthScore}
              </p>
              <ProjectStatusBadge status={project.status} />
            </div>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-xs uppercase tracking-[0.14em] text-slate-500">Commit Velocity</p>
            <p className="mt-2 text-[34px] font-semibold tracking-[-0.03em] text-slate-900">
              {project.commitVelocity}/wk
            </p>
          </div>
        </div>

        <div className="mt-5 rounded-2xl border border-slate-200 p-4">
          <ProjectProgress value={project.progress} />
        </div>
      </div>
    </div>
  );
}

