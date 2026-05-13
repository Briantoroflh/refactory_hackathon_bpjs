import { ApiClientError } from "@/lib/api/client";
import { getAIActionHint, mapAIError, validateAIPrompt } from "@/lib/ai/api";

export type AIIntegrationScenarioResult = {
  scenario: string;
  passed: boolean;
  details?: string;
};

function evaluateScenario(name: string, condition: boolean, details?: string): AIIntegrationScenarioResult {
  return {
    scenario: name,
    passed: condition,
    details,
  };
}

export function runAIPageIntegrationScenarios(): AIIntegrationScenarioResult[] {
  const results: AIIntegrationScenarioResult[] = [];

  const validPrompt = validateAIPrompt("Analisis blocker sprint ini");
  results.push(
    evaluateScenario(
      "valid prompt submit",
      validPrompt.ok,
      "Prompt valid harus lolos validasi sebelum request",
    ),
  );

  const invalidPrompt = validateAIPrompt("   ");
  results.push(
    evaluateScenario(
      "empty prompt blocked",
      !invalidPrompt.ok,
      "Prompt kosong harus diblok sebelum hit endpoint",
    ),
  );

  const authError = mapAIError(new ApiClientError("Not authenticated", 401));
  results.push(
    evaluateScenario(
      "401 actionable guidance",
      getAIActionHint(authError.status).toLowerCase().includes("login"),
      "401 harus memberi panduan login ulang",
    ),
  );

  const validationError = mapAIError(new ApiClientError("Validation failed", 422));
  results.push(
    evaluateScenario(
      "422 actionable guidance",
      getAIActionHint(validationError.status).toLowerCase().includes("prompt"),
      "422 harus memberi panduan perbaikan prompt",
    ),
  );

  const transientError = mapAIError(new ApiClientError("Server unavailable", 503));
  results.push(
    evaluateScenario(
      "5xx retry policy",
      transientError.retryable,
      "5xx harus ditandai retryable",
    ),
  );

  return results;
}
