"use client";

type MetricCard = {
  title: string;
  value: string;
  delta: string;
  tone?: "up" | "down" | "stable";
  icon: string;
};

type ProgressItem = {
  label: string;
  value: number;
  color: string;
};

type ActivityItem = {
  title: string;
  subtitle: string;
  time: string;
  tone: string;
};

const metrics: MetricCard[] = [
  { title: "Total Employees", value: "1,248", delta: "+2.4%", tone: "up", icon: "👥" },
  { title: "Active Admins", value: "24", delta: "Stable", tone: "stable", icon: "🛡️" },
  { title: "Open Requisitions", value: "18", delta: "-5", tone: "down", icon: "🧳" },
];

const composition: ProgressItem[] = [
  { label: "Engineering", value: 42, color: "#4f46e5" },
  { label: "Product", value: 21, color: "#0f766e" },
  { label: "Design", value: 15, color: "#8b5cf6" },
  { label: "Marketing", value: 22, color: "#f97316" },
];

const activities: ActivityItem[] = [
  { title: "Sarah Jenkins onboarded", subtitle: "Engineering Dept • 2 hrs ago", time: "new", tone: "emerald" },
  { title: "Q3 Performance Reviews initiated", subtitle: "System • 4 hrs ago", time: "pending", tone: "violet" },
  { title: "Maria Rodriguez promoted", subtitle: "Product Dept • 1 day ago", time: "done", tone: "amber" },
  { title: "Security Policies updated", subtitle: "Admin • 2 days ago", time: "updated", tone: "slate" },
];

const activityToneClasses: Record<string, string> = {
  emerald: "bg-emerald-100",
  violet: "bg-violet-100",
  amber: "bg-amber-100",
  slate: "bg-slate-100",
};

const kpis = [
  { label: "Average Productivity", value: "84%", delta: "+3%" },
  { label: "Sprint Velocity", value: "42 pts", delta: "Avg." },
  { label: "Code Quality Index", value: "92%", delta: "+1.2%" },
];

const navItems = [
  { label: "Dashboard", active: true, icon: "▣" },
  { label: "Users", icon: "👤" },
  { label: "Roles", icon: "🏷️" },
  { label: "Permissions", icon: "🔐" },
  { label: "Audit Logs", icon: "🧾" },
  { label: "Security", icon: "🛡️" },
];

function SectionCard({
  title,
  children,
  action,
}: {
  title: string;
  children: React.ReactNode;
  action?: React.ReactNode;
}) {
  return (
    <section className="rounded-[24px] border border-slate-200 bg-white p-5 shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
      <div className="mb-5 flex items-center justify-between">
        <h3 className="text-[18px] font-semibold tracking-[-0.02em] text-slate-900">{title}</h3>
        {action}
      </div>
      {children}
    </section>
  );
}

function Sidebar() {
  return (
    <aside className="flex h-full w-[280px] flex-col border-r border-slate-200 bg-[#f8f7ff] p-4">
      <div className="flex items-center gap-3 rounded-[18px] px-2 py-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-[#4f46e5] text-sm font-bold text-white">
          B
        </div>
        <div>
          <p className="text-[15px] font-semibold text-slate-900">Bloom HRM</p>
          <p className="text-[12px] text-slate-500">System Management</p>
        </div>
      </div>

      <button className="mt-4 rounded-2xl bg-[#4f46e5] px-4 py-3 text-left text-[14px] font-semibold text-white shadow-[0_12px_24px_rgba(79,70,229,0.2)]">
        + New Policy
      </button>

      <nav className="mt-5 space-y-1">
        {navItems.map((item) => (
          <a
            key={item.label}
            href="#"
            className={`flex items-center gap-3 rounded-2xl px-4 py-3 text-[14px] font-medium transition ${
              item.active ? "bg-[#ede9fe] text-[#4338ca]" : "text-slate-600 hover:bg-white"
            }`}
          >
            <span>{item.icon}</span>
            {item.label}
          </a>
        ))}
      </nav>

      <div className="mt-auto space-y-1 border-t border-slate-200 pt-4 text-[13px] text-slate-500">
        <a href="#" className="block rounded-2xl px-4 py-2 hover:bg-white">
          Documentation
        </a>
        <a href="#" className="block rounded-2xl px-4 py-2 hover:bg-white">
          Support
        </a>
      </div>
    </aside>
  );
}

export function DashboardPage() {
  return (
    <div className="min-h-screen bg-[#eef1f8] p-3 text-slate-900">
      <div className="mx-auto flex min-h-[calc(100vh-1.5rem)] w-full overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-[0_12px_38px_rgba(15,23,42,0.12)]">
        <Sidebar />

        <main className="min-w-0 flex-1 overflow-y-auto bg-[#f8f9fd] px-5 py-5 lg:px-8">
          <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <h1 className="text-[34px] font-semibold tracking-[-0.03em] text-slate-900">Workforce Intelligence</h1>
              <p className="mt-1 text-[15px] text-slate-500">Real-time insights into organizational health and activity.</p>
            </div>
            <div className="flex gap-3">
              <button className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-[14px] font-semibold text-slate-700">
                Export Report
              </button>
              <button className="rounded-2xl bg-[#4f46e5] px-4 py-3 text-[14px] font-semibold text-white shadow-[0_12px_24px_rgba(79,70,229,0.18)]">
                Filter
              </button>
            </div>
          </div>

          <div className="grid gap-4 xl:grid-cols-3">
            {metrics.map((metric) => (
              <article key={metric.title} className="rounded-[22px] border border-slate-200 bg-white p-5 shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
                <div className="mb-6 flex items-start justify-between">
                  <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[#eef2ff] text-[18px]">
                    {metric.icon}
                  </div>
                  <span
                    className={`rounded-full px-3 py-1 text-[12px] font-semibold ${
                      metric.tone === "up"
                        ? "bg-emerald-50 text-emerald-600"
                        : metric.tone === "down"
                          ? "bg-amber-50 text-amber-600"
                          : "bg-slate-100 text-slate-500"
                    }`}
                  >
                    {metric.delta}
                  </span>
                </div>
                <p className="text-[14px] text-slate-500">{metric.title}</p>
                <p className="mt-2 text-[30px] font-semibold tracking-[-0.03em] text-slate-900">{metric.value}</p>
              </article>
            ))}
          </div>

          <div className="mt-6 grid gap-6 xl:grid-cols-[1.1fr_1fr_0.9fr]">
            <SectionCard title="Workforce Composition">
              <div className="space-y-4">
                {composition.map((item) => (
                  <div key={item.label}>
                    <div className="mb-2 flex items-center justify-between text-[14px] font-medium text-slate-700">
                      <span>{item.label}</span>
                      <span>{item.value}%</span>
                    </div>
                    <div className="h-2 rounded-full bg-slate-100">
                      <div className="h-2 rounded-full" style={{ width: `${item.value}%`, backgroundColor: item.color }} />
                    </div>
                  </div>
                ))}
              </div>
            </SectionCard>

            <SectionCard
              title="Retention Trends"
              action={<span className="rounded-full bg-[#ede9fe] px-3 py-1 text-[12px] font-semibold text-[#4338ca]">YTD</span>}
            >
              <div className="flex h-[220px] items-end gap-3 rounded-[20px] bg-[#fbfbff] p-4">
                {[28, 40, 52, 38, 60, 74, 66, 82].map((height, index) => (
                  <div key={index} className="flex-1">
                    <div className="mx-auto rounded-t-lg bg-[#4f46e5]" style={{ height: `${height}%`, width: "100%" }} />
                  </div>
                ))}
              </div>
            </SectionCard>

            <SectionCard title="Recent HR Actions" action={<a href="#" className="text-[13px] font-semibold text-[#4338ca]">View All</a>}>
              <div className="space-y-4">
                {activities.map((item) => (
                  <div key={item.title} className="flex gap-3 rounded-[18px] border border-slate-100 bg-white p-3">
                    <div className={`mt-1 h-9 w-9 rounded-full ${activityToneClasses[item.tone] ?? "bg-slate-100"}`} />
                    <div className="min-w-0">
                      <p className="text-[14px] font-semibold text-slate-800">{item.title}</p>
                      <p className="text-[13px] text-slate-500">{item.subtitle}</p>
                    </div>
                  </div>
                ))}
              </div>
            </SectionCard>
          </div>

          <div className="mt-6 grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
            <SectionCard title="Engineering Performance KPIs" action={<span className="rounded-full bg-[#ede9fe] px-3 py-1 text-[12px] font-semibold text-[#4338ca]">This Month</span>}>
              <div className="grid gap-4 sm:grid-cols-3">
                {kpis.map((kpi) => (
                  <div key={kpi.label} className="rounded-[18px] border border-slate-200 bg-slate-50 p-4">
                    <p className="text-[13px] text-slate-500">{kpi.label}</p>
                    <div className="mt-2 flex items-end justify-between">
                      <p className="text-[28px] font-semibold tracking-[-0.03em] text-slate-900">{kpi.value}</p>
                      <span className="pb-1 text-[13px] font-semibold text-emerald-600">{kpi.delta}</span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-5 space-y-4">
                {[
                  { name: "Alex Johnson", pct: 98 },
                  { name: "Maria Lopez", pct: 94 },
                  { name: "Raka Pratama", pct: 89 },
                ].map((person) => (
                  <div key={person.name}>
                    <div className="mb-1 flex items-center justify-between text-[14px] font-medium text-slate-700">
                      <span>{person.name}</span>
                      <span>{person.pct}%</span>
                    </div>
                    <div className="h-2 rounded-full bg-slate-100">
                      <div className="h-2 rounded-full bg-[#4f46e5]" style={{ width: `${person.pct}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </SectionCard>

            <SectionCard title="AI Summary">
              <div className="space-y-4">
                <div className="rounded-[18px] bg-[#f8f7ff] p-4">
                  <p className="text-[14px] font-semibold text-slate-800">Workforce health is stable</p>
                  <p className="mt-1 text-[14px] leading-6 text-slate-500">
                    Attrition remains low, and engineering performance is trending upward.
                  </p>
                </div>
                <div className="rounded-[18px] bg-[#fff7ed] p-4">
                  <p className="text-[14px] font-semibold text-slate-800">Action needed</p>
                  <p className="mt-1 text-[14px] leading-6 text-slate-500">
                    Open requisitions in design need approval to avoid hiring delay.
                  </p>
                </div>
              </div>
            </SectionCard>
          </div>
        </main>
      </div>
    </div>
  );
}
