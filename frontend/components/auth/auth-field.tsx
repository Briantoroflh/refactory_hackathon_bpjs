import type { InputHTMLAttributes, ReactNode } from "react";
import { forwardRef, useId } from "react";

type AuthFieldProps = InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
  icon?: ReactNode;
  trailing?: ReactNode;
  error?: string;
  helperText?: string;
};

export const AuthField = forwardRef<HTMLInputElement, AuthFieldProps>(function AuthField(
  { className = "", label, icon, trailing, error, helperText, id, ...props },
  ref,
) {
  const generatedId = useId();
  const fieldId = id ?? generatedId;
  const errorId = error ? `${fieldId}-error` : undefined;
  const helperId = helperText ? `${fieldId}-helper` : undefined;

  return (
    <div className="space-y-3">
      {label ? (
        <label htmlFor={fieldId} className="block text-[16px] font-semibold tracking-[-0.02em] text-slate-950 sm:text-[18px]">
          {label}
        </label>
      ) : null}
      <div
        className={`flex min-h-14 items-center gap-3 rounded-[18px] border border-slate-200 bg-white px-4 shadow-[0_1px_0_rgba(15,23,42,0.02)] transition focus-within:border-[#5648ea]/40 focus-within:ring-4 focus-within:ring-[#5648ea]/8 sm:min-h-16 ${className} ${
          error ? "border-rose-300 focus-within:border-rose-400 focus-within:ring-rose-100" : ""
        }`}
      >
        {icon ? <span className="shrink-0 text-[#8b90a6]">{icon}</span> : null}
        <input
          ref={ref}
          id={fieldId}
          aria-invalid={Boolean(error)}
          aria-describedby={[errorId, helperId].filter(Boolean).join(" ") || undefined}
          className="h-full w-full border-0 bg-transparent text-[15px] text-slate-900 placeholder:text-slate-400 focus:outline-none sm:text-[16px]"
          {...props}
        />
        {trailing ? <span className="shrink-0 text-[#8b90a6]">{trailing}</span> : null}
      </div>
      {helperText ? (
        <p id={helperId} className="text-sm text-slate-500">
          {helperText}
        </p>
      ) : null}
      {error ? (
        <p id={errorId} className="text-sm font-medium text-rose-500">
          {error}
        </p>
      ) : null}
    </div>
  );
});
