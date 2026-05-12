export type LoginFormValues = {
  email: string;
  password: string;
  rememberMe: boolean;
};

export type LoginFormErrors = Partial<Record<keyof LoginFormValues | "form", string>>;

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function createInitialLoginValues(): LoginFormValues {
  return {
    email: "",
    password: "",
    rememberMe: true,
  };
}

export function validateLoginValues(values: LoginFormValues): LoginFormErrors {
  const errors: LoginFormErrors = {};

  if (!values.email.trim()) {
    errors.email = "Email is required.";
  } else if (!EMAIL_PATTERN.test(values.email.trim())) {
    errors.email = "Enter a valid email address.";
  }

  if (!values.password) {
    errors.password = "Password is required.";
  } else if (values.password.length < 8) {
    errors.password = "Password must be at least 8 characters.";
  }

  return errors;
}

export function hasValidationErrors(errors: LoginFormErrors): boolean {
  return Object.values(errors).some(Boolean);
}
