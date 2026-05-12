export function DashboardSkeleton() {
  return (
    <div className="min-h-screen bg-[#f3f5fb] p-4">
      <div className="mx-auto max-w-[1400px] rounded-[24px] border border-slate-200 bg-white p-4 shadow-[0_10px_40px_rgba(15,23,42,0.08)]">
        <div className="grid gap-6 xl:grid-cols-[290px_1fr]">
          <div className="hidden h-[calc(100vh-2rem)] rounded-[24px] bg-slate-100 lg:block" />
          <div className="space-y-6">
            <div className="h-[84px] rounded-[20px] bg-slate-100" />
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {Array.from({ length: 4 }).map((_, index) => (
                <div key={index} className="h-[150px] rounded-[22px] bg-slate-100" />
              ))}
            </div>
            <div className="grid gap-6 xl:grid-cols-[1.6fr_0.92fr]">
              <div className="h-[420px] rounded-[24px] bg-slate-100" />
              <div className="h-[420px] rounded-[24px] bg-slate-100" />
            </div>
            <div className="h-[280px] rounded-[24px] bg-slate-100" />
          </div>
        </div>
      </div>
    </div>
  );
}
