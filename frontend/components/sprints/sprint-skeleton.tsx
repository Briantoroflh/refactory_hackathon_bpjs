export function SprintSkeleton() {
  return (
    <div className="min-h-screen bg-[#eef1f8] p-3 sm:p-4 animate-in fade-in duration-500">
      <div className="mx-auto grid min-h-[calc(100vh-1.5rem)] overflow-hidden rounded-[26px] border border-slate-200 bg-white lg:grid-cols-[286px_1fr]">
        {/* Sidebar Skeleton */}
        <div className="hidden bg-[#f3f1fb] lg:block p-5 space-y-8">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-slate-200 animate-pulse" />
            <div className="space-y-2">
              <div className="h-4 w-20 bg-slate-200 animate-pulse rounded" />
              <div className="h-3 w-24 bg-slate-200 animate-pulse rounded" />
            </div>
          </div>
          <div className="space-y-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-12 w-full bg-slate-200/50 animate-pulse rounded-2xl" />
            ))}
          </div>
        </div>

        {/* Main Content Skeleton */}
        <div className="space-y-6 p-4 sm:p-8">
          {/* Header Skeleton */}
          <div className="flex justify-between items-start">
            <div className="space-y-3">
              <div className="h-10 w-64 bg-slate-100 animate-pulse rounded-xl" />
              <div className="h-5 w-48 bg-slate-100 animate-pulse rounded-lg" />
            </div>
            <div className="flex gap-3">
              <div className="h-11 w-32 bg-slate-100 animate-pulse rounded-xl" />
              <div className="h-11 w-32 bg-slate-100 animate-pulse rounded-xl" />
            </div>
          </div>

          {/* Progress Skeleton */}
          <div className="space-y-3 rounded-[24px] border border-slate-100 p-6">
            <div className="flex justify-between">
              <div className="h-4 w-24 bg-slate-100 animate-pulse rounded" />
              <div className="h-4 w-12 bg-slate-100 animate-pulse rounded" />
            </div>
            <div className="h-3 w-full bg-slate-100 animate-pulse rounded-full" />
          </div>

          {/* Stat Cards Skeleton */}
          <div className="grid gap-4 sm:grid-cols-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-32 rounded-2xl bg-slate-50 border border-slate-100 animate-pulse" />
            ))}
          </div>

          {/* Kanban Board Skeleton */}
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {Array.from({ length: 4 }).map((_, index) => (
              <div key={index} className="space-y-4 rounded-3xl bg-slate-50 p-4 border border-slate-100">
                <div className="flex justify-between items-center mb-2">
                  <div className="h-6 w-20 bg-slate-200 animate-pulse rounded" />
                  <div className="h-8 w-8 rounded-full bg-slate-200 animate-pulse" />
                </div>
                {Array.from({ length: 2 }).map((_, j) => (
                  <div key={j} className="h-40 w-full bg-white rounded-2xl border border-slate-100 animate-pulse" />
                ))}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

