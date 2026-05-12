import type { SprintStat, SprintSummary } from "@/lib/sprints/types";
import { CalendarIcon, PlusIcon, SparkleIcon } from "./sprint-icons";

type SprintOverviewProps = {
  sprint: SprintSummary;
  progress: number;
  onCreateSprint: () => void;
  onOpenCreateTask: () => void;
};

type SprintStatCardsProps = {
  stats: SprintStat[];
};

const toneClass: Record<NonNullable<SprintStat["tone"]>, string> = {
  default: "text-slate-800",
  success: "text-emerald-500",
  warning: "text-amber-500",
};

export function SprintOverview({
  sprint,
  progress,
  onCreateSprint,
  onOpenCreateTask,
}: SprintOverviewProps) {
  return (
    <section className="rounded-[24px] border border-slate-200 bg-white p-5 sm:p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-[34px] leading-tight font-semibold tracking-[-0.04em] text-slate-800 sm:text-[42px]">
            {sprint.name}
          </h1>
          <p className="mt-2 inline-flex items-center gap-2 text-[17px] text-slate-600 sm:text-[21px]">
            <CalendarIcon className="h-5 w-5" />
            {sprint.startDateLabel} - {sprint.endDateLabel} ({sprint.daysRemaining} days remaining)
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          <button className="rounded-xl bg-[#e9e8f4] px-5 py-2.5 text-[15px] font-semibold text-slate-700">
            Complete Sprint
          </button>
          <button
            type="button"
            onClick={onCreateSprint}
            className="inline-flex items-center gap-2 rounded-xl bg-[#3f2fd6] px-5 py-2.5 text-[15px] font-semibold text-white shadow-[0_12px_24px_rgba(67,56,202,0.26)]"
          >
            <SparkleIcon className="h-4 w-4" />
            Create Sprint
          </button>
          <button
            type="button"
            onClick={onOpenCreateTask}
            className="inline-flex items-center gap-2 rounded-xl border border-[#cfd5eb] bg-white px-5 py-2.5 text-[15px] font-semibold text-slate-700"
          >
            <PlusIcon className="h-4 w-4" />
            Create Task
          </button>
        </div>
      </div>

      <div className="mt-5">
        <div className="flex items-center justify-between text-[14px] font-semibold text-slate-500">
          <span>Sprint Progress</span>
          <span>{progress}%</span>
        </div>
        <div className="mt-2 h-3 overflow-hidden rounded-full bg-[#e7e9f6]">
          <div
            className="h-full rounded-full bg-[linear-gradient(90deg,#4f46e5,#2563eb)] transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    </section>
  );
}

export function SprintStatCards({ stats }: SprintStatCardsProps) {
  return (
    <section className="rounded-[24px] border border-slate-200 bg-white p-5 sm:p-6">
      <header className="mb-5 flex items-center justify-between">
        <h2 className="text-[20px] font-semibold tracking-[-0.02em] text-slate-800">Burndown Chart</h2>
        <span className="text-2xl text-slate-500">•••</span>
      </header>

      <div className="grid gap-3 sm:grid-cols-3">
        {stats.map((stat) => (
          <article key={stat.id} className="rounded-2xl border border-[#dedff0] bg-[#f2f1fb] p-4">
            <p className="text-[14px] font-semibold text-slate-500">{stat.label}</p>
            <p
              className={`mt-2 text-[31px] font-semibold tracking-[-0.03em] ${toneClass[stat.tone ?? "default"]}`}
            >
              {stat.value}
            </p>
          </article>
        ))}
      </div>

      <div className="mt-5 rounded-2xl border border-[#dde2f1] bg-[#f4f2fd] p-4">
        <div className="relative h-[170px] rounded-xl bg-[repeating-linear-gradient(to_bottom,transparent_0,transparent_32px,#d9def0_32px,#d9def0_34px)]">
          <div className="absolute inset-x-4 top-5 h-px border-t border-dashed border-[#ced6ee]" />
          <div className="absolute left-[6%] top-[25%] h-px w-[88%] -rotate-[18deg] border-t border-dashed border-[#d7ddef]" />
          <div className="absolute right-[18%] bottom-[30%] h-3 w-3 rounded-full bg-[#4f46e5]" />
        </div>
      </div>
    </section>
  );
}
