export default function Loading() {
  return (
    <div className="space-y-6 p-8 animate-pulse">
      <div className="h-12 w-1/3 rounded-lg bg-slate-200" />
      <div className="grid gap-6 lg:grid-cols-[1fr_340px]">
        <div className="h-96 rounded-lg bg-slate-200" />
        <div className="h-96 rounded-lg bg-slate-200" />
      </div>
    </div>
  );
}
