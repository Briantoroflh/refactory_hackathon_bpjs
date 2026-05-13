import { ApiClientError } from "@/lib/api/client";
import {
  AIAssistantError,
  AI_MAX_PROMPT_LENGTH,
  getAIActionHint,
  mapAIError,
  normalizeAIResponse,
  validateAIPrompt,
} from "@/lib/ai/api";

type AssertionResult = {
  name: string;
  passed: boolean;
  message?: string;
};

function assert(name: string, condition: boolean, message?: string): AssertionResult {
  return {
    name,
    passed: condition,
    message,
  };
}

export function runAIValidationUnitChecks(): AssertionResult[] {
  const results: AssertionResult[] = [];

  const empty = validateAIPrompt("   ");
  results.push(assert("reject-empty-prompt", !empty.ok, "Prompt kosong harus ditolak"));

  const tooLong = validateAIPrompt("a".repeat(AI_MAX_PROMPT_LENGTH + 1));
  results.push(assert("reject-too-long-prompt", !tooLong.ok, "Prompt terlalu panjang harus ditolak"));

  const valid = validateAIPrompt("  ringkas sprint aktif  ");
  results.push(assert("accept-valid-prompt", valid.ok, "Prompt valid harus diterima"));

  const normalized = normalizeAIResponse({ content: "ok" });
  results.push(
    assert(
      "normalize-default-fields",
      normalized.workflow === "unknown" && normalized.model === "unknown" && normalized.content === "ok",
      "Response default fields harus terisi",
    ),
  );

  const mapped401 = mapAIError(new ApiClientError("Not authenticated", 401));
  results.push(assert("map-401", mapped401.code === "AUTH_REQUIRED" && !mapped401.retryable));

  const mapped422 = mapAIError(new ApiClientError("Validation failed", 422));
  results.push(assert("map-422", mapped422.code === "VALIDATION_FAILED" && !mapped422.retryable));

  const mapped500 = mapAIError(new ApiClientError("Server busy", 500));
  results.push(assert("map-500-retryable", mapped500.retryable, "5xx harus retryable"));

  const mappedTimeout = mapAIError({ name: "AbortError", message: "aborted" } as Error);
  results.push(assert("map-timeout", mappedTimeout.code === "REQUEST_TIMEOUT"));

  const explicit = mapAIError(new AIAssistantError("x", 503, true, "TRANSIENT_FAILURE"));
  results.push(assert("map-existing-ai-error", explicit.code === "TRANSIENT_FAILURE"));

  results.push(assert("hint-401", getAIActionHint(401).toLowerCase().includes("login")));
  results.push(assert("hint-422", getAIActionHint(422).toLowerCase().includes("prompt")));

  return results;
}
