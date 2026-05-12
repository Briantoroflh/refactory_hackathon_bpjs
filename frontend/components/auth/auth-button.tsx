import type { ButtonHTMLAttributes, ReactNode } from "react";

type AuthButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode;
};

export function AuthButton({ className = "", children, ...props }: AuthButtonProps) {
  return (
    <button
      className={`inline-flex h-16 w-full items-center justify-center gap-2 rounded-[20px] bg-[#5648ea] px-6 text-[18px] font-semibold tracking-[-0.02em] text-white shadow-[0_16px_30px_rgba(86,72,234,0.28)] transition-transform duration-200 hover:-translate-y-0.5 hover:bg-[#4c3ee4] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#5648ea]/30 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-70 ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
