"use client";

import { BloomMarkIcon } from "../auth/icons";

export function SplashScreen() {
  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-[#f5f7fb] overflow-hidden">
      {/* Premium Mesh Gradient Background (Light Theme) */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-5%] w-[60%] h-[60%] bg-[#3f35d6]/5 rounded-full blur-[100px] animate-mesh" />
        <div className="absolute bottom-[-10%] right-[-5%] w-[60%] h-[60%] bg-[#2f2fd9]/5 rounded-full blur-[100px] animate-mesh" style={{ animationDelay: '-5s' }} />
        <div className="absolute top-[30%] right-[15%] w-[30%] h-[30%] bg-[#402edd]/5 rounded-full blur-[80px] animate-mesh" style={{ animationDelay: '-10s' }} />
      </div>

      <div className="relative flex flex-col items-center z-10">
        {/* Futuristic Logo Container */}
        <div className="relative mb-12 group animate-scale-in">
          {/* Animated Glow Rings */}
          <div className="absolute inset-[-15px] rounded-full bg-gradient-to-tr from-[#3f35d6] to-[#2f2fd9] opacity-10 blur-xl animate-pulse" />
          
          {/* Main Logo Card with Premium Glassmorphism */}
          <div className="relative rounded-[32px] bg-white px-10 py-9 border border-slate-200 shadow-[0_20px_50px_rgba(47,47,217,0.08)]">
            <div className="relative">
              <BloomMarkIcon className="h-24 w-24 text-[#2f2fd9]" />
              {/* Shimmer effect on logo */}
              <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-[#2f2fd9]/10 to-transparent skew-x-12 translate-x-[-200%] animate-[shimmer_3s_infinite]" />
            </div>
          </div>
        </div>

        {/* Content with Elegant Typography */}
        <div className="text-center space-y-6 max-w-xs">
          <div className="space-y-2">
            <h1 className="text-4xl font-extrabold tracking-tight text-[#0b1020] animate-fade-in" style={{ animationDelay: '0.3s', opacity: 0 }}>
              Bloom<span className="text-[#2f2fd9]">OS</span>
            </h1>
            <div className="flex justify-center gap-1 animate-fade-in" style={{ animationDelay: '0.5s', opacity: 0 }}>
              <div className="h-1.5 w-10 bg-[#2f2fd9] rounded-full" />
              <div className="h-1.5 w-3 bg-[#2f2fd9]/40 rounded-full" />
              <div className="h-1.5 w-1.5 bg-[#2f2fd9]/20 rounded-full" />
            </div>
          </div>
          
          <p className="text-slate-500 text-sm font-medium tracking-wide leading-relaxed animate-fade-in" style={{ animationDelay: '0.7s', opacity: 0 }}>
            Elevating your engineering workflow with AI-powered intelligence
          </p>
          
          {/* Premium Loading Section */}
          <div className="pt-8 space-y-4 animate-fade-in" style={{ animationDelay: '0.9s', opacity: 0 }}>
            <div className="relative w-64 h-2 bg-slate-200/50 rounded-full overflow-hidden mx-auto border border-slate-200/50">
              {/* Animated Progress Track */}
              <div className="absolute inset-0 bg-gradient-to-r from-[#3f35d6] via-[#2f2fd9] to-[#4330dc] animate-progress" />
            </div>
            
            <div className="flex items-center justify-center gap-3">
              <div className="flex gap-1.5">
                <span className="w-1.5 h-1.5 bg-[#2f2fd9] rounded-full animate-bounce" style={{ animationDelay: '0s' }} />
                <span className="w-1.5 h-1.5 bg-[#2f2fd9] rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                <span className="w-1.5 h-1.5 bg-[#2f2fd9] rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
              </div>
              <span className="text-[11px] text-[#2f2fd9] font-bold uppercase tracking-[0.3em]">
                Synchronizing
              </span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Minimalist Tech Footer */}
      <div className="absolute bottom-12 animate-fade-in" style={{ animationDelay: '1.2s', opacity: 0 }}>
        <div className="px-8 py-3 rounded-2xl border border-slate-200 bg-white/50 backdrop-blur-sm shadow-sm">
          <p className="text-[10px] text-slate-400 font-bold uppercase tracking-[0.4em] flex items-center gap-3">
            <span className="w-2 h-2 rounded-full bg-[#2f2fd9] animate-pulse" />
            Powered by Bloom AI
          </p>
        </div>
      </div>

      {/* Subtle Grain Overlay */}
      <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.03] pointer-events-none mix-blend-multiply" />
      <div className="absolute inset-0 bg-[radial-gradient(#2f2fd910_1.5px,transparent_1.5px)] [background-size:48px_48px] pointer-events-none" />
    </div>
  );
}
