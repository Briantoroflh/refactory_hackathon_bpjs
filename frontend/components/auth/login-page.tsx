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
            <BloomMarkIcon className="h-10 w-10 lg:h-12 lg:w-12" />
            <span className="text-[20px] font-medium tracking-[-0.02em] text-white lg:text-[22px]">Bloom</span>
          </div>

          <div className="absolute inset-x-0 bottom-0 top-1/3 bg-[radial-gradient(circle_at_20%_72%,rgba(255,255,255,0.15),transparent_20%),radial-gradient(circle_at_68%_58%,rgba(255,255,255,0.09),transparent_18%),radial-gradient(circle_at_42%_88%,rgba(255,255,255,0.13),transparent_24%)] opacity-80" />
          <div className="absolute bottom-20 left-10 right-10 h-[36rem] rounded-[2.5rem] border border-white/10 bg-[linear-gradient(145deg,rgba(255,255,255,0.06),transparent_42%,rgba(255,255,255,0.04)_100%)] blur-0 lg:h-[42rem]" />

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
              Bloom OS
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
