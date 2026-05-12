/**
 * Test API connectivity
 */
export async function testAPIConnection() {
  try {
    const url = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/docs`;
    console.log(`Testing API connection to: ${url}`);

    const response = await fetch(url);
    if (response.ok) {
      console.log("✅ API is reachable and responding");
      return { success: true, status: response.status };
    } else {
      console.error(`❌ API responded with status: ${response.status}`);
      return { success: false, status: response.status };
    }
  } catch (error) {
    console.error("❌ Failed to connect to API:", error);
    return {
      success: false,
      error: error instanceof Error ? error.message : String(error),
    };
  }
}

/**
 * Test login endpoint
 */
export async function testLoginEndpoint(
  email: string = "test@example.com",
  password: string = "test123",
) {
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const url = `${apiUrl}/auth/login`;

    console.log(`Testing login endpoint: ${url}`);

    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    console.log(`Response status: ${response.status}`);

    if (response.status === 200) {
      const data = await response.json();
      console.log("✅ Login endpoint working:", data);
      return { success: true, status: 200, data };
    } else if (response.status === 401 || response.status === 422) {
      console.log(
        "✅ Login endpoint reachable (invalid credentials - expected)",
      );
      return {
        success: true,
        status: response.status,
        message: "Endpoint working (invalid credentials)",
      };
    } else {
      const error = await response.text();
      console.error(`❌ Unexpected response: ${error}`);
      return { success: false, status: response.status, error };
    }
  } catch (error) {
    console.error("❌ Failed to test login:", error);
    return {
      success: false,
      error: error instanceof Error ? error.message : String(error),
    };
  }
}

/**
 * Run all connection tests
 */
export async function runConnectivityTests() {
  console.log("\n🧪 Running API Connectivity Tests\n");

  const apiTest = await testAPIConnection();
  console.log(
    `API Connection: ${apiTest.success ? "✅ PASS" : "❌ FAIL"}`,
    apiTest,
  );

  if (apiTest.success) {
    const loginTest = await testLoginEndpoint();
    console.log(
      `\nLogin Endpoint: ${loginTest.success ? "✅ PASS" : "❌ FAIL"}`,
      loginTest,
    );
  }

  console.log("\n");
}
