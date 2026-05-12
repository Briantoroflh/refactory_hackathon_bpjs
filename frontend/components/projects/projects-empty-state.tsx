type ProjectsEmptyStateProps = {
  title: string;
  description: string;
};

export function ProjectsEmptyState({ title, description }: ProjectsEmptyStateProps) {
  return (
    <div className="rounded-[20px] border border-dashed border-slate-300 bg-white px-6 py-10 text-center">
      <p className="text-[22px] font-semibold tracking-[-0.02em] text-slate-800">{title}</p>
      <p className="mx-auto mt-2 max-w-lg text-[16px] text-slate-500">{description}</p>
    </div>
  );
}

