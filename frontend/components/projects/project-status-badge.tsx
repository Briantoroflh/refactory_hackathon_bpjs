import type { ProjectStatus } from "@/lib/projects/types";

type ProjectStatusBadgeProps = {
  status: ProjectStatus;
};

export function ProjectStatusBadge({ status }: ProjectStatusBadgeProps) {
  const styleMap: Record<ProjectStatus, string> = {
    healthy: "bg-emerald-50 text-emerald-600 border-emerald-200",
    warning: "bg-amber-50 text-amber-600 border-amber-200",
    critical: "bg-rose-50 text-rose-600 border-rose-200",
  };

  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-[12px] font-semibold capitalize ${styleMap[status]}`}>
      {status}
    </span>
  );
}

