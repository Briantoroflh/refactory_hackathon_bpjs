export default function Loading() {
  return (
    <div className="min-h-screen bg-slate-50 p-4 sm:p-6 lg:p-8">
      <div className="mx-auto grid max-w-[1200px] gap-6 xl:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)]">
        <div className="h-64 rounded-2xl border border-slate-200 bg-white" />
        <div className="h-64 rounded-2xl border border-slate-200 bg-white" />
      </div>
    </div>
  );
}
