import type { InputHTMLAttributes } from "react";

type AuthCheckboxProps = InputHTMLAttributes<HTMLInputElement> & {
  label: string;
};

export function AuthCheckbox({ className = "", label, ...props }: AuthCheckboxProps) {
  return (
    <label className="inline-flex items-center gap-3 text-[15px] text-slate-700 sm:text-[16px]">
      <input
        type="checkbox"
        className={`h-5 w-5 rounded-[5px] border border-slate-300 text-[#5648ea] focus:ring-[#5648ea]/30 ${className}`}
        {...props}
      />
      <span>{label}</span>
    </label>
  );
}
