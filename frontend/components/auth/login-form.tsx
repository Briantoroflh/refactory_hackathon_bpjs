"use client";

import type { FormEvent } from "react";
import { useState } from "react";
import { AuthButton } from "./auth-button";
import { AuthCheckbox } from "./auth-checkbox";
import { AuthField } from "./auth-field";
import { ArrowRightIcon, EyeIcon, EyeOffIcon, LockIcon, MailIcon, ShieldIcon } from "./icons";
import { login } from "@/lib/auth/api";
import {
  createInitialLoginValues,
  hasValidationErrors,
  type LoginFormErrors,
  type LoginFormValues,
  validateLoginValues,
} from "@/lib/auth/validation";
import { useRouter } from "next/navigation";

export function LoginForm() {
  const router = useRouter();
  const [values, setValues] = useState<LoginFormValues>(() => createInitialLoginValues());
  const [errors, setErrors] = useState<LoginFormErrors>({});
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [status, setStatus] = useState<{ type: 'success' | 'error', message: string } | null>(null);

  const emailError = errors.email;
  const passwordError = errors.password;
  const formError = errors.form;

  function updateField<K extends keyof LoginFormValues>(key: K, value: LoginFormValues[K]) {
    setValues((current) => ({ ...current, [key]: value }));
    setErrors((current) => ({ ...current, [key]: undefined }));
    setStatus(null);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const nextErrors = validateLoginValues(values);
    setErrors(nextErrors);
    setStatus(null);

    if (hasValidationErrors(nextErrors)) {
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await login(values);
      setStatus({ type: 'success', message: "Sign in successful! Redirecting..." });
      
      // Store token if needed (though usually handled in api.ts or middleware)
      // Redirect to dashboard on success
      setTimeout(() => {
        router.push("/dashboard");
      }, 1000);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unable to sign in.";
      setStatus({ type: 'error', message });
      setErrors({ form: message });
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="space-y-7" onSubmit={handleSubmit} noValidate>
      <AuthField
        label="Email address"
        type="email"
        name="email"
        autoComplete="email"
        placeholder="name@company.com"
        value={values.email}
        onChange={(event) => updateField("email", event.target.value)}
        icon={<MailIcon className="h-6 w-6" />}
        error={emailError}
      />

      <div className="space-y-3">
        <div className="flex items-center justify-between gap-4">
          <label htmlFor="password" className="block text-[16px] font-semibold tracking-[-0.02em] text-slate-950 sm:text-[18px]">
            Password
          </label>
          <a href="/forgot-password" className="text-[14px] font-semibold text-[#5648ea] transition hover:text-[#4338ca] sm:text-[16px]">
            Forgot password?
          </a>
        </div>
        <AuthField
          id="password"
          type={showPassword ? "text" : "password"}
          name="password"
          autoComplete="current-password"
          placeholder="••••••••••"
          value={values.password}
          onChange={(event) => updateField("password", event.target.value)}
          icon={<LockIcon className="h-6 w-6" />}
          trailing={
            <button
              type="button"
              onClick={() => setShowPassword((current) => !current)}
              aria-label={showPassword ? "Hide password" : "Show password"}
              className="inline-flex h-8 w-8 items-center justify-center rounded-full text-[#8b90a6] transition hover:bg-slate-100 hover:text-slate-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#5648ea]/30"
            >
              {showPassword ? <EyeOffIcon className="h-5 w-5" /> : <EyeIcon className="h-5 w-5" />}
            </button>
          }
          error={passwordError}
        />
      </div>

      <div className="flex items-center justify-between gap-6">
        <AuthCheckbox
          label="Keep me logged in"
          checked={values.rememberMe}
          onChange={(event) => updateField("rememberMe", event.target.checked)}
        />
      </div>

      {formError ? (
        <p className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-600">
          {formError}
        </p>
      ) : null}

      {status ? (
        <p className={`rounded-2xl border px-4 py-3 text-sm font-medium ${
          status.type === 'success' ? 'border-emerald-200 bg-emerald-50 text-emerald-700' : 'border-rose-200 bg-rose-50 text-rose-600'
        }`}>
          {status.message}
        </p>
      ) : null}

      <AuthButton type="submit" disabled={isSubmitting}>
        <span>{isSubmitting ? "Signing in..." : "Sign In"}</span>
        <ArrowRightIcon className="h-5 w-5" />
      </AuthButton>

      <div className="border-t border-slate-200 pt-8 text-center">
        <div className="inline-flex items-center gap-2 text-[13px] font-semibold uppercase tracking-[0.22em] text-slate-400 sm:text-[14px]">
          <ShieldIcon className="h-4 w-4" />
          <span>Secure corporate portal</span>
        </div>
      </div>
    </form>
  );
}
