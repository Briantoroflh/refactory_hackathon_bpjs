export default function Loading() {
  return (
    <div className="flex h-screen bg-slate-50">
      {/* Sidebar skeleton */}
      <div className="hidden w-[280px] border-r border-slate-200 bg-white lg:block">
        <div className="h-[88px] border-b border-slate-100" />
        <div className="space-y-2 px-3 py-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div
              key={i}
              className="h-10 rounded-xl bg-slate-100 animate-pulse"
            />
          ))}
        </div>
      </div>

      <div className="flex flex-1 flex-col">
        {/* Navbar skeleton */}
        <div className="flex h-[82px] items-center gap-4 border-b border-slate-200 bg-white px-4 sm:px-6 lg:px-8">
          <div className="h-11 w-11 rounded-2xl bg-slate-100 animate-pulse lg:hidden" />
          <div className="hidden h-6 w-48 rounded bg-slate-100 animate-pulse md:block" />
          <div className="ml-auto h-11 w-80 rounded-full bg-slate-100 animate-pulse" />
          <div className="hidden gap-3 sm:flex">
            {Array.from({ length: 3 }).map((_, i) => (
              <div
                key={i}
                className="h-11 w-11 rounded-full bg-slate-100 animate-pulse"
              />
            ))}
          </div>
        </div>

        {/* Content skeleton */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          <div className="space-y-6">
            <div className="space-y-2">
              <div className="h-8 w-64 rounded bg-slate-100 animate-pulse" />
              <div className="h-5 w-96 rounded bg-slate-100 animate-pulse" />
            </div>

            <div className="h-12 w-full rounded bg-slate-100 animate-pulse" />

            <div className="space-y-4">
              <div className="h-6 w-48 rounded bg-slate-100 animate-pulse" />
              <div className="grid gap-3 md:grid-cols-3">
                {Array.from({ length: 3 }).map((_, i) => (
                  <div
                    key={i}
                    className="h-24 rounded-lg bg-slate-100 animate-pulse"
                  />
                ))}
              </div>
            </div>

            <div className="space-y-4">
              <div className="h-6 w-48 rounded bg-slate-100 animate-pulse" />
              {Array.from({ length: 2 }).map((_, i) => (
                <div
                  key={i}
                  className="h-20 rounded-lg bg-slate-100 animate-pulse"
                />
              ))}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
