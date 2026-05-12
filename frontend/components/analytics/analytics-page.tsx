"use client";
import { AppLayout } from "@/components/layout/app-layout";
import type {
  TeamAnalytics,
  EngineerPerformance,
  AIInsight,
} from "@/lib/analytics/types";

type AnalyticsPageProps = {
  analytics: TeamAnalytics;
  notice?: string | null;
};

function PerformanceMetrics({ score }: { score: number }) {
  const getColor = (s: number) => {
    if (s >= 9) return "text-emerald-500";
    if (s >= 8) return "text-blue-500";
    return "text-amber-500";
  };

  return (
    <span className={`font-semibold ${getColor(score)}`}>
      {score.toFixed(1)}
    </span>
  );
}

function StatusBadge({ status }: { status: string }) {
  const variants = {
    optimal: "bg-emerald-50 text-emerald-700 border-emerald-200",
    warning: "bg-amber-50 text-amber-700 border-amber-200",
    critical: "bg-rose-50 text-rose-700 border-rose-200",
  };
  return (
    <span
      className={`inline-flex rounded-full border px-2.5 py-0.5 text-[12px] font-semibold capitalize ${
        variants[status as keyof typeof variants]
      }`}
    >
      ● {status}
    </span>
  );
}

function EngineerTable({ engineers }: { engineers: EngineerPerformance[] }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white overflow-hidden">
      <table className="w-full">
        <thead>
          <tr className="border-b border-slate-200 bg-slate-50">
            <th className="px-6 py-3 text-left text-[12px] font-semibold text-slate-600 uppercase tracking-wider">
              Engineer
            </th>
            <th className="px-6 py-3 text-left text-[12px] font-semibold text-slate-600 uppercase tracking-wider">
              Velocity
            </th>
            <th className="px-6 py-3 text-left text-[12px] font-semibold text-slate-600 uppercase tracking-wider">
              Quality
            </th>
            <th className="px-6 py-3 text-left text-[12px] font-semibold text-slate-600 uppercase tracking-wider">
              Score
            </th>
            <th className="px-6 py-3 text-left text-[12px] font-semibold text-slate-600 uppercase tracking-wider">
              Status
            </th>
          </tr>
        </thead>
        <tbody>
          {engineers.map((engineer, index) => (
            <tr
              key={engineer.id}
              className={`border-b border-slate-100 ${index === engineers.length - 1 ? "" : ""}`}
            >
              <td className="px-6 py-4">
                <div className="flex items-center gap-3">
                  <div className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-[#4338ca] text-white text-[12px] font-bold">
                    {engineer.avatar}
                  </div>
                  <div>
                    <div className="text-[14px] font-semibold text-slate-800">
                      {engineer.name}
                    </div>
                    <div className="text-[12px] text-slate-500">
                      {engineer.role}
                    </div>
                  </div>
                </div>
              </td>
              <td className="px-6 py-4">
                <div className="text-[14px] font-semibold text-slate-800">
                  {engineer.velocity} pts
                </div>
              </td>
              <td className="px-6 py-4">
                <div className="text-[14px] font-semibold text-slate-800">
                  {engineer.quality}%
                </div>
              </td>
              <td className="px-6 py-4">
                <PerformanceMetrics score={engineer.score} />
              </td>
              <td className="px-6 py-4">
                <StatusBadge status={engineer.status} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function AIInsightCard({ insight }: { insight: AIInsight }) {
  const severityStyles = {
    info: "bg-blue-50 border-blue-200 text-blue-900",
    warning: "bg-amber-50 border-amber-200 text-amber-900",
    critical: "bg-rose-50 border-rose-200 text-rose-900",
  };

  const severityIndicator = {
    info: "bg-blue-500",
    warning: "bg-amber-500",
    critical: "bg-rose-500",
  };

  return (
    <div
      className={`rounded-xl border p-4 ${
        severityStyles[insight.severity as keyof typeof severityStyles]
      }`}
    >
      <div className="flex items-start gap-3">
        <div
          className={`mt-1 h-2 w-2 rounded-full shrink-0 ${
            severityIndicator[
              insight.severity as keyof typeof severityIndicator
            ]
          }`}
        />
        <div className="flex-1">
          <h4 className="text-[14px] font-semibold mb-1">{insight.title}</h4>
          <p className="text-[13px] leading-relaxed">{insight.description}</p>
        </div>
      </div>
    </div>
  );
}

export function AnalyticsPage({ analytics, notice }: AnalyticsPageProps) {
  const sprintInfo =
    analytics.sprintLabel ??
    `Sprint ${analytics.sprintNumber} • ${analytics.quarter} ${analytics.year} Analytics`;
  const breadcrumbs = [
    { label: "Team Analytics" },
    { label: sprintInfo }
  ];

  return (
    <AppLayout title="Team Performance" breadcrumbs={breadcrumbs}>
      <div className="space-y-6">
        {notice ? (
          <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-[14px] font-medium text-amber-800">
            {notice}
          </div>
        ) : null}

        {/* Sprint Info / Header Extra */}
        <div className="flex items-center justify-between gap-4 -mt-2 mb-2">
          <p className="text-[16px] font-medium text-slate-500">{sprintInfo}</p>
          <button className="inline-flex items-center gap-2 rounded-xl bg-[#4338ca] px-6 py-3 text-[14px] font-bold text-white hover:bg-[#3f2fd6] transition shadow-[0_10px_24px_rgba(67,56,202,0.25)]">
            Export
          </button>
        </div>

        {/* Team Velocity Card */}
        <div className="rounded-[24px] border border-slate-200 bg-white p-6 shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-[15px] font-semibold text-slate-500 uppercase tracking-wider">
                Team Velocity
              </h2>
              <div className="mt-3 flex items-baseline gap-2">
                <div className="text-5xl font-bold tracking-tight text-slate-900">
                  {analytics.teamVelocity.current}
                </div>
                <div className="text-[15px] font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-lg border border-emerald-100">
                  ↑ {analytics.teamVelocity.trend}%
                </div>
              </div>
              <p className="mt-3 text-[14px] font-medium text-slate-600">
                {analytics.teamVelocity.completedPoints} story points
                completed this sprint
              </p>
            </div>
            <div className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-[#f3ecfc] text-[#4338ca] shadow-[0_8px_16px_rgba(67,56,202,0.1)]">
              📈
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Engineer Performance */}
          <div className="lg:col-span-2">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-[20px] font-bold tracking-tight text-slate-900">
                Engineer Performance
              </h2>
              <button className="text-[14px] font-semibold text-[#4338ca] hover:underline">
                View All →
              </button>
            </div>
            <EngineerTable engineers={analytics.engineers} />
          </div>

          {/* AI Insights */}
          <div>
            <div className="mb-4 flex items-center gap-2">
              <span className="text-xl">✨</span>
              <h2 className="text-[20px] font-bold tracking-tight text-slate-900">
                AI Insights
              </h2>
            </div>
            <div className="space-y-4">
              {analytics.insights.map((insight) => (
                <AIInsightCard key={insight.id} insight={insight} />
              ))}
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
