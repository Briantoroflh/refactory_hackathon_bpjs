"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { SplashScreen } from "@/components/ui/splash-screen";

export default function Home() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setMounted(true);
    
    // Simulasi loading selama 2.5 detik
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 2500);

    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (mounted && !isLoading) {
      router.push("/login");
    }
  }, [mounted, isLoading, router]);

  if (!mounted) return null;

  return isLoading ? <SplashScreen /> : null;
}
