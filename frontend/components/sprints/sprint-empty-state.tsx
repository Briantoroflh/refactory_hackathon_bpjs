type SprintEmptyStateProps = {
  title: string;
  description: string;
};

export function SprintEmptyState({ title, description }: SprintEmptyStateProps) {
  return (
    <div className="rounded-[24px] border border-dashed border-[#cfd5ea] bg-white p-10 text-center">
      <h3 className="text-lg font-semibold text-slate-700">{title}</h3>
      <p className="mx-auto mt-2 max-w-xl text-[15px] text-slate-500">{description}</p>
    </div>
  );
}

