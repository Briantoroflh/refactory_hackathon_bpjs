export function ProjectsSkeleton() {
  return (
    <div className="min-h-screen bg-[#f3f5fb] p-4">
      <div className="grid min-h-[calc(100vh-2rem)] overflow-hidden rounded-[24px] border border-slate-200 bg-white lg:grid-cols-[286px_1fr]">
        <div className="hidden bg-[#f3f1fb] lg:block" />
        <div className="space-y-5 p-4 sm:p-6">
          <div className="h-[84px] rounded-2xl bg-slate-100" />
          <div className="h-28 rounded-2xl bg-slate-100" />
          <div className="grid gap-4 xl:grid-cols-3">
            {Array.from({ length: 3 }).map((_, index) => (
              <div key={index} className="h-[280px] rounded-2xl bg-slate-100" />
            ))}
          </div>
          <div className="h-[280px] rounded-2xl bg-slate-100" />
        </div>
      </div>
    </div>
  );
}

