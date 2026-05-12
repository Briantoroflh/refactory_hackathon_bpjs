import type { ProjectItem } from "@/lib/projects/types";
import { DotsIcon, RepoIcon } from "./project-icons";
import { ProjectProgress } from "./project-progress";
import { ProjectStatusBadge } from "./project-status-badge";

type ProjectCardProps = {
  project: ProjectItem;
  onOpenDetail: (projectId: string) => void;
};

export function ProjectCard({ project, onOpenDetail }: ProjectCardProps) {
  const healthColor =
    project.aiHealthScore >= 85 ? "text-emerald-500" : project.aiHealthScore >= 70 ? "text-amber-500" : "text-rose-500";

  return (
    <article className="rounded-[18px] border border-slate-200 bg-white p-5 shadow-[0_10px_22px_rgba(15,23,42,0.04)]">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-[#f1eefc] text-[#4f46e5]">
            <RepoIcon className="h-6 w-6" />
          </div>
          <div>
            <button
              type="button"
              onClick={() => onOpenDetail(project.id)}
              className="text-left text-[20px] font-semibold leading-[1.2] tracking-[-0.03em] text-slate-800 transition hover:text-[#4338ca]"
            >
              {project.name}
            </button>
            <p className="mt-1 text-[14px] font-medium text-slate-500">{project.platform}</p>
          </div>
        </div>
        <button className="text-slate-500 transition hover:text-slate-700" aria-label="More options">
          <DotsIcon className="h-6 w-6" />
        </button>
      </div>

      <div className="mt-6 grid grid-cols-2 gap-4 border-b border-slate-200 pb-5">
        <div>
          <p className="text-[13px] uppercase tracking-[0.12em] text-slate-500">AI Health Score</p>
          <div className="mt-1 flex items-center gap-2">
            <span className={`text-[32px] font-semibold tracking-[-0.03em] ${healthColor}`}>
              {project.aiHealthScore}
            </span>
            <ProjectStatusBadge status={project.status} />
          </div>
        </div>
        <div>
          <p className="text-[13px] uppercase tracking-[0.12em] text-slate-500">Commit Velocity</p>
          <p className="mt-1 text-[18px] font-semibold text-slate-800">{project.commitVelocity}/wk</p>
          <div className="mt-2 flex items-end gap-1">
            {project.commitBars.map((value, index) => (
              <span
                key={index}
                className={`w-3 rounded-sm ${index % 2 === 0 ? "bg-[#c9c2f4]" : "bg-[#6f5ce8]"}`}
                style={{ height: `${Math.max(value, 8)}px` }}
              />
            ))}
          </div>
        </div>
      </div>

      <div className="mt-4">
        <ProjectProgress value={project.progress} />
      </div>

      <div className="mt-4 flex items-center justify-between">
        <div className="flex -space-x-2">
          {project.members.slice(0, 3).map((member) => (
            <div
              key={member.id}
              title={member.name}
              className="inline-flex h-9 w-9 items-center justify-center rounded-full border-2 border-white bg-[linear-gradient(180deg,#334155,#0f172a)] text-xs font-semibold text-white"
            >
              {member.avatar}
            </div>
          ))}
          {project.members.length > 3 ? (
            <div className="inline-flex h-9 w-9 items-center justify-center rounded-full border-2 border-white bg-slate-200 text-xs font-semibold text-slate-600">
              +{project.members.length - 3}
            </div>
          ) : null}
        </div>
        <p className="text-[13px] font-medium text-slate-500">{project.updatedAtLabel}</p>
      </div>
    </article>
  );
}
