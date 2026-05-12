export function SprintSkeleton() {
  return (
    <div className="min-h-screen bg-[#eef1f8] p-3 sm:p-4">
      <div className="mx-auto grid min-h-[calc(100vh-1.5rem)] overflow-hidden rounded-[26px] border border-slate-200 bg-white lg:grid-cols-[286px_1fr]">
        <div className="hidden bg-[#f3f1fb] lg:block" />
        <div className="space-y-5 p-4 sm:p-6">
          <div className="h-[82px] rounded-2xl bg-slate-100" />
          <div className="h-[190px] rounded-2xl bg-slate-100" />
          <div className="h-[280px] rounded-2xl bg-slate-100" />
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {Array.from({ length: 4 }).map((_, index) => (
              <div key={index} className="h-[230px] rounded-2xl bg-slate-100" />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

