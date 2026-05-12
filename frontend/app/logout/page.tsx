"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { logout } from "@/lib/auth/api";

export default function LogoutPage() {
  const router = useRouter();

  useEffect(() => {
    logout();
    router.push("/login");
  }, [router]);

  return (
    <div className="flex h-screen w-full items-center justify-center bg-[#f3f5fb]">
      <div className="flex flex-col items-center gap-4">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-[#4338ca] border-t-transparent" />
        <p className="text-[16px] font-bold text-slate-600">Signing out...</p>
      </div>
    </div>
  );
}
