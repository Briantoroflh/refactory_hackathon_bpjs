"use client";

import Link from "next/link";
import { BloomMarkIcon } from "./icons";
import { LoginForm } from "./login-form";

export function LoginPage() {
  return (
    <div className="min-h-screen bg-[#f5f7fb] text-slate-900 md:grid md:grid-cols-[1.08fr_0.92fr]">
      <aside className="relative hidden overflow-hidden bg-[linear-gradient(180deg,#3f35d6_0%,#402edd_38%,#4330dc_100%)] md:flex">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_28%_18%,rgba(126,118,255,0.35),transparent_24%),radial-gradient(circle_at_72%_34%,rgba(92,82,241,0.24),transparent_24%),radial-gradient(circle_at_42%_76%,rgba(134,126,255,0.2),transparent_28%),linear-gradient(180deg,rgba(255,255,255,0.08),rgba(255,255,255,0))]" />
        <div className="absolute inset-0 bg-[linear-gradient(150deg,transparent_0%,transparent_36%,rgba(255,255,255,0.08)_36%,transparent_37%,transparent_58%,rgba(255,255,255,0.07)_58%,transparent_59%)] opacity-70" />
        <div className="relative flex w-full flex-col justify-between px-12 py-10 lg:px-16 lg:py-14">
          <div className="relative z-10 flex items-center gap-5 text-[#0b1020]">
            <BloomMarkIcon className="h-10 w-10 text-white lg:h-12 lg:w-12" />
            <span className="text-[22px] font-bold tracking-[-0.02em] text-white lg:text-[24px]">Bloom<span className="text-blue-300">OS</span></span>
          </div>

          <div className="relative z-10 flex flex-col justify-center">
            <div className="max-w-md animate-fade-in" style={{ animationDelay: '0.2s' }}>
              <h2 className="text-[32px] font-bold leading-[1.2] tracking-[-0.03em] text-white lg:text-[42px]">
                The Intelligent OS for <span className="text-blue-300">Modern Engineering.</span>
              </h2>
              <p className="mt-6 text-[16px] leading-relaxed text-blue-100/80 lg:text-[18px]">
                Streamline your workflow, track performance, and ship faster with our AI-powered engineering platform.
              </p>
            </div>

            <div className="mt-12 grid grid-cols-1 gap-6 animate-fade-in lg:mt-16" style={{ animationDelay: '0.4s' }}>
              <div className="flex items-start gap-4 rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-sm transition-all hover:bg-white/10">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-400/20 text-blue-300">
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-[15px] font-semibold text-white">Rapid Deployment</h3>
                  <p className="mt-1 text-[13px] text-blue-100/60">Automate your CI/CD pipeline with ease.</p>
                </div>
              </div>

              <div className="flex items-start gap-4 rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-sm transition-all hover:bg-white/10">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-indigo-400/20 text-indigo-300">
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-[15px] font-semibold text-white">Advanced Analytics</h3>
                  <p className="mt-1 text-[13px] text-blue-100/60">Real-time insights into team productivity.</p>
                </div>
              </div>
            </div>
          </div>

          <div className="relative z-10">
            <div className="max-w-sm text-white/90">
              <p className="text-[14px] font-medium tracking-[0.18em] text-white/85 lg:text-[15px]">
                © 2024 Bloom Engineering OS
              </p>
              <div className="mt-5 flex items-center gap-6 text-[14px] font-medium text-white/85 lg:gap-8 lg:text-[15px]">
                <Link href="/privacy" className="transition hover:text-white">
                  Privacy
                </Link>
                <Link href="/terms" className="transition hover:text-white">
                  Terms
                </Link>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <main className="flex min-h-screen items-start justify-center px-4 py-8 sm:px-6 sm:py-10 md:items-center md:px-8 lg:px-12">
        <div className="flex w-full max-w-[500px] flex-col items-center">
          <div className="mt-2 flex flex-col items-center gap-4 md:mt-0">
            <div className="rounded-[20px] border border-slate-200 bg-white px-5 py-4 shadow-[0_10px_24px_rgba(15,23,42,0.05)]">
              <BloomMarkIcon className="h-14 w-14 text-black" />
            </div>
            <p className="text-[18px] font-medium tracking-[-0.02em] text-[#2f2fd9]">
              Bloom
            </p>
          </div>

          <section className="mt-8 w-full rounded-[34px] border border-slate-200 bg-white px-7 py-8 shadow-[0_22px_55px_rgba(15,23,42,0.06)] sm:px-9 sm:py-10">
            <header className="space-y-2.5">
              <h1 className="text-[24px] font-medium tracking-[-0.03em] text-slate-950 sm:text-[26px]">
                Welcome back
              </h1>
              <p className="text-[17px] tracking-[-0.02em] text-slate-500 sm:text-[18px]">
                Access your engineering dashboard.
              </p>
            </header>

            <div className="mt-8">
              <LoginForm />
            </div>
          </section>

          <div className="mt-8 flex items-center gap-6 text-[14px] text-slate-400 md:hidden">
            <Link href="/security">Security</Link>
            <span>•</span>
            <Link href="/help">Help Center</Link>
            <span>•</span>
            <Link href="/status">System Status</Link>
          </div>

          <div className="mt-8 hidden items-center gap-12 text-[14px] text-slate-400 md:flex">
            <Link href="/security">Security</Link>
            <span>•</span>
            <Link href="/help">Help Center</Link>
            <span>•</span>
            <Link href="/status">System Status</Link>
          </div>
        </div>
      </main>
    </div>
  );
}
