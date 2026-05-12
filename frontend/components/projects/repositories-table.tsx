import type { RepositoryConnection } from "@/lib/projects/types";

type RepositoriesTableProps = {
  repositories: RepositoryConnection[];
};

export function RepositoriesTable({ repositories }: RepositoriesTableProps) {
  return (
    <section className="overflow-hidden rounded-[18px] border border-slate-200 bg-white shadow-[0_8px_20px_rgba(15,23,42,0.04)]">
      <header className="flex items-center justify-between border-b border-slate-200 px-5 py-4">
        <h2 className="text-[28px] font-semibold tracking-[-0.03em] text-slate-800">
          Connected Repositories
        </h2>
        <button className="text-[16px] font-semibold text-[#4338ca]">Manage Connections</button>
      </header>

      <div className="overflow-x-auto">
        <table className="min-w-full">
          <thead className="bg-[#f4f1fd] text-left">
            <tr className="text-[13px] uppercase tracking-[0.14em] text-slate-500">
              <th className="px-5 py-4 font-semibold">Repository Name</th>
              <th className="px-5 py-4 font-semibold">Platform</th>
              <th className="px-5 py-4 font-semibold">Status</th>
              <th className="px-5 py-4 font-semibold">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {repositories.map((repository) => (
              <tr key={repository.id} className="text-[17px] text-slate-700">
                <td className="px-5 py-4 font-medium text-slate-800">{repository.repositoryName}</td>
                <td className="px-5 py-4">{repository.platform}</td>
                <td className="px-5 py-4">
                  <StatusPill status={repository.status} />
                </td>
                <td className="px-5 py-4">
                  <button className="rounded-lg border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-600">
                    Manage
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function StatusPill({ status }: { status: RepositoryConnection["status"] }) {
  const styles = {
    syncing: "bg-emerald-50 text-emerald-600 border-emerald-200",
    paused: "bg-slate-100 text-slate-600 border-slate-200",
    failed: "bg-rose-50 text-rose-600 border-rose-200",
  };
  return <span className={`inline-flex rounded-full border px-3 py-1 text-sm font-semibold capitalize ${styles[status]}`}>{status}</span>;
}
