type ProjectProgressProps = {
  value: number;
};

export function ProjectProgress({ value }: ProjectProgressProps) {
  const normalized = Math.max(0, Math.min(100, value));
  return (
    <div className="space-y-1">
      <div className="h-2 w-full rounded-full bg-slate-100">
        <div
          className="h-2 rounded-full bg-[linear-gradient(90deg,#5b4bf2,#4338ca)]"
          style={{ width: `${normalized}%` }}
        />
      </div>
      <p className="text-[12px] font-medium text-slate-500">Progress {normalized}%</p>
    </div>
  );
}

