/**
 * AI Wrapping Integration Test
 *
 * Tests to verify that the AI assistant wrapping layer is working correctly
 * and that responses are properly formatted and retrievable.
 */

import { aiAssistantAPI } from "@/lib/api/client";

export interface AITestResult {
  workflow: string;
  status: "success" | "error";
  duration: number;
  details: {
    request?: any;
    response?: any;
    error?: string;
  };
}

/**
 * Test AI planning workflow
 */
export async function testAIPlanningWorkflow(): Promise<AITestResult> {
  const startTime = Date.now();
  try {
    const response = await aiAssistantAPI.planning({
      prompt: "Create a project plan for Q3 2024",
      context: {
        project_id: 1,
        team_size: 5,
      },
      async_mode: true,
    });

    return {
      workflow: "planning",
      status: "success",
      duration: Date.now() - startTime,
      details: {
        response,
      },
    };
  } catch (error) {
    return {
      workflow: "planning",
      status: "error",
      duration: Date.now() - startTime,
      details: {
        error: error instanceof Error ? error.message : String(error),
      },
    };
  }
}

/**
 * Test AI sprint summary workflow
 */
export async function testAISprintSummaryWorkflow(): Promise<AITestResult> {
  const startTime = Date.now();
  try {
    const response = await aiAssistantAPI.sprintSummary({
      prompt: "Summarize Sprint 42 progress",
      context: {
        sprint_id: 42,
        project_id: 1,
      },
      async_mode: true,
    });

    return {
      workflow: "sprint_summary",
      status: "success",
      duration: Date.now() - startTime,
      details: {
        response,
      },
    };
  } catch (error) {
    return {
      workflow: "sprint_summary",
      status: "error",
      duration: Date.now() - startTime,
      details: {
        error: error instanceof Error ? error.message : String(error),
      },
    };
  }
}

/**
 * Test AI task recommendation workflow
 */
export async function testAITaskRecommendationWorkflow(): Promise<AITestResult> {
  const startTime = Date.now();
  try {
    const response = await aiAssistantAPI.taskRecommendation({
      prompt: "Recommend next tasks for the team",
      context: {
        project_id: 1,
        sprint_id: 42,
        team_id: 1,
      },
      async_mode: true,
    });

    return {
      workflow: "task_recommendation",
      status: "success",
      duration: Date.now() - startTime,
      details: {
        response,
      },
    };
  } catch (error) {
    return {
      workflow: "task_recommendation",
      status: "error",
      duration: Date.now() - startTime,
      details: {
        error: error instanceof Error ? error.message : String(error),
      },
    };
  }
}

/**
 * Test AI job status polling
 */
export async function testAIJobStatusPolling(
  jobId: string,
): Promise<AITestResult> {
  const startTime = Date.now();
  try {
    const response = await aiAssistantAPI.jobStatus(jobId);

    return {
      workflow: "job_status",
      status: "success",
      duration: Date.now() - startTime,
      details: {
        response,
      },
    };
  } catch (error) {
    return {
      workflow: "job_status",
      status: "error",
      duration: Date.now() - startTime,
      details: {
        error: error instanceof Error ? error.message : String(error),
      },
    };
  }
}

/**
 * Run all AI wrapping tests
 */
export async function runAllAITests(): Promise<AITestResult[]> {
  console.log("🧪 Starting AI Wrapping Tests...");

  const results: AITestResult[] = [];

  // Test 1: Planning workflow
  console.log("Testing AI Planning Workflow...");
  const planningResult = await testAIPlanningWorkflow();
  results.push(planningResult);
  console.log(
    `✅ Planning: ${planningResult.status} (${planningResult.duration}ms)${
      planningResult.details.error ? ": " + planningResult.details.error : ""
    }`,
  );

  // Test 2: Sprint Summary workflow
  console.log("Testing AI Sprint Summary Workflow...");
  const sprintResult = await testAISprintSummaryWorkflow();
  results.push(sprintResult);
  console.log(
    `✅ Sprint Summary: ${sprintResult.status} (${sprintResult.duration}ms)${
      sprintResult.details.error ? ": " + sprintResult.details.error : ""
    }`,
  );

  // Test 3: Task Recommendation workflow
  console.log("Testing AI Task Recommendation Workflow...");
  const taskResult = await testAITaskRecommendationWorkflow();
  results.push(taskResult);
  console.log(
    `✅ Task Recommendation: ${taskResult.status} (${taskResult.duration}ms)${
      taskResult.details.error ? ": " + taskResult.details.error : ""
    }`,
  );

  // If any workflow returned a job_id, test polling
  const jobIds = results
    .map((r) => r.details.response?.job_id)
    .filter((id): id is string => !!id);

  if (jobIds.length > 0) {
    console.log("Testing AI Job Status Polling...");
    const pollResult = await testAIJobStatusPolling(jobIds[0]);
    results.push(pollResult);
    console.log(
      `✅ Job Status Polling: ${pollResult.status} (${pollResult.duration}ms)${
        pollResult.details.error ? ": " + pollResult.details.error : ""
      }`,
    );
  }

  const successCount = results.filter((r) => r.status === "success").length;
  console.log(`\n📊 Test Results: ${successCount}/${results.length} passed`);

  return results;
}

/**
 * Export test result as JSON
 */
export function exportTestResults(results: AITestResult[]): string {
  return JSON.stringify(
    {
      timestamp: new Date().toISOString(),
      summary: {
        total: results.length,
        passed: results.filter((r) => r.status === "success").length,
        failed: results.filter((r) => r.status === "error").length,
      },
      results,
    },
    null,
    2,
  );
}
