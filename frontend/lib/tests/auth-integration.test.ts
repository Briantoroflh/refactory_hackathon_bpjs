import type { LoginFormValues } from "@/lib/auth/validation";

export type AuthTestResult = {
  test: string;
  status: "pass" | "fail";
  message: string;
  duration: number;
};

/**
 * Test auth API configuration and environment
 */
async function testAuthConfig(): Promise<AuthTestResult> {
  const start = Date.now();
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const authKey = process.env.NEXT_PUBLIC_AUTH_STORAGE_KEY || "access_token";

    if (!apiUrl) {
      throw new Error("NEXT_PUBLIC_API_URL not configured");
    }

    console.log(`✓ API URL: ${apiUrl}`);
    console.log(`✓ Auth storage key: ${authKey}`);

    return {
      test: "Auth Configuration",
      status: "pass",
      message: `API configured correctly at ${apiUrl}`,
      duration: Date.now() - start,
    };
  } catch (error) {
    return {
      test: "Auth Configuration",
      status: "fail",
      message: error instanceof Error ? error.message : String(error),
      duration: Date.now() - start,
    };
  }
}

/**
 * Test auth login endpoint connectivity
 */
async function testAuthLoginEndpoint(): Promise<AuthTestResult> {
  const start = Date.now();
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    // Test with invalid credentials to verify endpoint exists
    const response = await fetch(`${apiUrl}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: "test@example.com",
        password: "wrongpassword",
      }),
    });

    // We expect 401 (unauthorized) or 422 (validation) if endpoint exists
    if (response.status === 404) {
      throw new Error("Auth login endpoint not found (404)");
    }

    if (response.status === 500) {
      const error = await response.text();
      throw new Error(`Server error: ${error}`);
    }

    console.log(
      `✓ Auth login endpoint responded with status ${response.status}`,
    );

    return {
      test: "Auth Login Endpoint",
      status: "pass",
      message: `Endpoint accessible (HTTP ${response.status})`,
      duration: Date.now() - start,
    };
  } catch (error) {
    return {
      test: "Auth Login Endpoint",
      status: "fail",
      message: error instanceof Error ? error.message : String(error),
      duration: Date.now() - start,
    };
  }
}

/**
 * Test token storage mechanism
 */
async function testTokenStorage(): Promise<AuthTestResult> {
  const start = Date.now();
  try {
    if (typeof window === "undefined") {
      throw new Error("localStorage not available (SSR context)");
    }

    const testToken = "test-jwt-token-" + Date.now();
    const storageKey =
      process.env.NEXT_PUBLIC_AUTH_STORAGE_KEY || "access_token";

    localStorage.setItem(storageKey, testToken);
    const retrieved = localStorage.getItem(storageKey);

    if (retrieved !== testToken) {
      throw new Error("Token storage/retrieval mismatch");
    }

    localStorage.removeItem(storageKey);

    console.log(`✓ Token storage working correctly`);

    return {
      test: "Token Storage",
      status: "pass",
      message: "localStorage tokens stored and retrieved correctly",
      duration: Date.now() - start,
    };
  } catch (error) {
    return {
      test: "Token Storage",
      status: "fail",
      message: error instanceof Error ? error.message : String(error),
      duration: Date.now() - start,
    };
  }
}

/**
 * Test auth API imports and functions exist
 */
async function testAuthAPIFunctions(): Promise<AuthTestResult> {
  const start = Date.now();
  try {
    const { login, logout, getStoredToken, isAuthenticated } =
      await import("@/lib/auth/api");

    if (typeof login !== "function")
      throw new Error("login function not found");
    if (typeof logout !== "function")
      throw new Error("logout function not found");
    if (typeof getStoredToken !== "function")
      throw new Error("getStoredToken function not found");
    if (typeof isAuthenticated !== "function")
      throw new Error("isAuthenticated function not found");

    console.log(`✓ All auth API functions available`);

    return {
      test: "Auth API Functions",
      status: "pass",
      message: "All required auth functions are exported",
      duration: Date.now() - start,
    };
  } catch (error) {
    return {
      test: "Auth API Functions",
      status: "fail",
      message: error instanceof Error ? error.message : String(error),
      duration: Date.now() - start,
    };
  }
}

/**
 * Test auth hooks API functions exist
 */
async function testAuthHooksFunctions(): Promise<AuthTestResult> {
  const start = Date.now();
  try {
    const { useAuth, useLazyLogin, useLazyRegister, authAPI } =
      await import("@/lib/api/auth");

    if (typeof useAuth !== "function")
      throw new Error("useAuth hook not found");
    if (typeof useLazyLogin !== "function")
      throw new Error("useLazyLogin hook not found");
    if (typeof useLazyRegister !== "function")
      throw new Error("useLazyRegister hook not found");
    if (typeof authAPI.login !== "function")
      throw new Error("authAPI.login not found");
    if (typeof authAPI.logout !== "function")
      throw new Error("authAPI.logout not found");

    console.log(`✓ All auth hooks available`);

    return {
      test: "Auth Hooks API",
      status: "pass",
      message: "All required auth hooks are exported",
      duration: Date.now() - start,
    };
  } catch (error) {
    return {
      test: "Auth Hooks API",
      status: "fail",
      message: error instanceof Error ? error.message : String(error),
      duration: Date.now() - start,
    };
  }
}

/**
 * Run all auth tests
 */
export async function runAllAuthTests(): Promise<AuthTestResult[]> {
  console.log("\n🧪 Starting Auth API Integration Tests\n");

  const tests = [
    testAuthConfig,
    testAuthLoginEndpoint,
    testTokenStorage,
    testAuthAPIFunctions,
    testAuthHooksFunctions,
  ];

  const results: AuthTestResult[] = [];

  for (const test of tests) {
    try {
      const result = await test();
      results.push(result);
      const icon = result.status === "pass" ? "✅" : "❌";
      console.log(
        `${icon} ${result.test}: ${result.message} (${result.duration}ms)`,
      );
    } catch (error) {
      console.error(`Error running test:`, error);
    }
  }

  const passed = results.filter((r) => r.status === "pass").length;
  const failed = results.filter((r) => r.status === "fail").length;
  const totalDuration = results.reduce((sum, r) => sum + r.duration, 0);

  console.log(
    `\n📊 Results: ${passed} passed, ${failed} failed (${totalDuration}ms total)\n`,
  );

  return results;
}

/**
 * Export test results as formatted string
 */
export function exportAuthTestResults(results: AuthTestResult[]): string {
  let output = "# Auth API Integration Test Results\n\n";

  for (const result of results) {
    const status = result.status === "pass" ? "✅ PASS" : "❌ FAIL";
    output += `## ${status} - ${result.test}\n`;
    output += `- Message: ${result.message}\n`;
    output += `- Duration: ${result.duration}ms\n\n`;
  }

  const passed = results.filter((r) => r.status === "pass").length;
  const failed = results.filter((r) => r.status === "fail").length;
  output += `## Summary\n`;
  output += `- Total Tests: ${results.length}\n`;
  output += `- Passed: ${passed}\n`;
  output += `- Failed: ${failed}\n`;
  output += `- Success Rate: ${((passed / results.length) * 100).toFixed(1)}%\n`;

  return output;
}
