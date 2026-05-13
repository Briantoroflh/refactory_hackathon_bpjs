import Link from "next/link";
import { AppLayout } from "@/components/layout/app-layout";

const shortcuts = [
  { label: "Projects", href: "/projects", note: "Open workspaces and status" },
  { label: "Tasks", href: "/tasks", note: "Drag, drop, and update status" },
  { label: "Sprint", href: "/sprints", note: "View active sprint board" },
  { label: "Profile", href: "/profile", note: "Update your account details" },
];

export default function HomePage() {
  return (
    <AppLayout title="Dashboard">
      <div className="space-y-6">
        <section className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
          <p className="text-[14px] font-semibold uppercase tracking-[0.18em] text-[#4338ca]">
            User Workspace
          </p>
          <h1 className="mt-2 text-[30px] font-semibold tracking-[-0.03em] text-slate-900">
            Welcome back
          </h1>
          <p className="mt-2 max-w-2xl text-[15px] leading-7 text-slate-500">
            Use this dashboard for day-to-day work. Project and task views stay tied to the live backend,
            while the HRM dashboard remains under the admin route.
          </p>
        </section>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {shortcuts.map((item) => (
            <Link
              key={item.label}
              href={item.href}
              className="rounded-[24px] border border-slate-200 bg-white p-5 shadow-[0_12px_28px_rgba(15,23,42,0.05)] transition hover:-translate-y-0.5 hover:shadow-[0_16px_32px_rgba(15,23,42,0.08)]"
            >
              <p className="text-[18px] font-semibold text-slate-900">{item.label}</p>
              <p className="mt-2 text-[14px] leading-6 text-slate-500">{item.note}</p>
            </Link>
          ))}
        </section>

        <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
            <h2 className="text-[20px] font-semibold tracking-[-0.02em] text-slate-900">
              Live status
            </h2>
            <div className="mt-5 grid gap-4 sm:grid-cols-3">
              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-[13px] text-slate-500">Assigned tasks</p>
                <p className="mt-2 text-[28px] font-semibold text-slate-900">12</p>
              </div>
              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-[13px] text-slate-500">Open reviews</p>
                <p className="mt-2 text-[28px] font-semibold text-slate-900">4</p>
              </div>
              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-[13px] text-slate-500">Active projects</p>
                <p className="mt-2 text-[28px] font-semibold text-slate-900">3</p>
              </div>
            </div>
          </div>

          <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
            <h2 className="text-[20px] font-semibold tracking-[-0.02em] text-slate-900">
              Quick notes
            </h2>
            <ul className="mt-5 space-y-3 text-[14px] leading-6 text-slate-500">
              <li>• Click Tasks to update work status with drag and drop.</li>
              <li>• Click Projects to review live backend data.</li>
              <li>• HRM admin dashboard is still available at /dashboard.</li>
            </ul>
          </div>
        </section>
      </div>
    </AppLayout>
  );
}
