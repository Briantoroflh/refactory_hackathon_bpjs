#!/usr/bin/env python3
"""
Load Testing Script for GitLab Integration Dashboard

Tests performance of dashboard metrics endpoints under load.
Verifies response times meet SLA: < 500ms for typical queries, < 2s for heavy queries.
"""

import asyncio
import time
from datetime import datetime, timedelta
import statistics
import httpx


class LoadTestConfig:
    """Configuration for load testing."""
    
    BASE_URL = "http://localhost:8000"
    BEARER_TOKEN = None  # Set via environment or command line
    PROJECT_ID = 1  # Default project ID
    
    # Test scenarios
    SCENARIOS = {
        "frequency": {
            "endpoint": "/api/v1/dashboard/gitlab-metrics/{project_id}/frequency",
            "params": {"days": 30},
            "timeout": 0.5,  # 500ms SLA
            "concurrent": 5,
        },
        "velocity": {
            "endpoint": "/api/v1/dashboard/gitlab-metrics/{project_id}/velocity",
            "params": {"days": 30},
            "timeout": 0.5,  # 500ms SLA
            "concurrent": 5,
        },
        "health": {
            "endpoint": "/api/v1/dashboard/gitlab-metrics/{project_id}/health",
            "params": {},
            "timeout": 0.5,  # 500ms SLA
            "concurrent": 5,
        },
        "full_metrics": {
            "endpoint": "/api/v1/dashboard/gitlab-metrics/{project_id}",
            "params": {"days": 30},
            "timeout": 2.0,  # 2s SLA for comprehensive metrics
            "concurrent": 3,
        },
        "commit_list": {
            "endpoint": "/api/v1/commits",
            "params": {"project_id": "{project_id}", "days": 30, "limit": 100},
            "timeout": 1.0,  # 1s SLA
            "concurrent": 5,
        },
    }


async def test_endpoint(client: httpx.AsyncClient, url: str, name: str, timeout: float):
    """Test a single endpoint."""
    start = time.time()
    try:
        response = await client.get(url, timeout=timeout)
        duration = time.time() - start
        
        if response.status_code == 200:
            return {
                "success": True,
                "duration": duration,
                "status": response.status_code,
                "error": None,
            }
        else:
            return {
                "success": False,
                "duration": duration,
                "status": response.status_code,
                "error": f"HTTP {response.status_code}",
            }
    except asyncio.TimeoutError:
        duration = time.time() - start
        return {
            "success": False,
            "duration": duration,
            "status": None,
            "error": "Timeout",
        }
    except Exception as e:
        duration = time.time() - start
        return {
            "success": False,
            "duration": duration,
            "status": None,
            "error": str(e),
        }


async def run_load_test(scenario_name: str, config: dict, token: str, project_id: int):
    """Run load test for a specific scenario."""
    print(f"\n{'=' * 80}")
    print(f"Testing: {scenario_name}")
    print(f"{'=' * 80}")
    
    endpoint = config["endpoint"].replace("{project_id}", str(project_id))
    url_template = f"{LoadTestConfig.BASE_URL}{endpoint}"
    params = {k: str(v).replace("{project_id}", str(project_id)) for k, v in config["params"].items()}
    
    concurrent = config["concurrent"]
    timeout = config["timeout"]
    
    print(f"Endpoint: {endpoint}")
    print(f"Parameters: {params}")
    print(f"Concurrent requests: {concurrent}")
    print(f"Timeout (SLA): {timeout:.1f}s")
    print()
    
    results = []
    
    async with httpx.AsyncClient() as client:
        # Run concurrent requests
        tasks = []
        for i in range(concurrent):
            task = test_endpoint(
                client,
                url_template,
                scenario_name,
                timeout,
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
    
    # Analyze results
    print("Results:")
    print("-" * 80)
    
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    print(f"Successful: {len(successful)}/{len(results)}")
    print(f"Failed: {len(failed)}/{len(results)}")
    print()
    
    if successful:
        durations = [r["duration"] for r in successful]
        print("Response Times (successful requests):")
        print(f"  Min:    {min(durations):.3f}s")
        print(f"  Max:    {max(durations):.3f}s")
        print(f"  Avg:    {statistics.mean(durations):.3f}s")
        if len(durations) > 1:
            print(f"  Median: {statistics.median(durations):.3f}s")
            print(f"  Stdev: {statistics.stdev(durations):.3f}s")
        print()
        
        # Check SLA
        sla_violations = [d for d in durations if d > timeout]
        if sla_violations:
            print(f"⚠ SLA VIOLATIONS: {len(sla_violations)} requests exceeded {timeout:.1f}s")
            for d in sla_violations:
                print(f"   - {d:.3f}s")
        else:
            print(f"✓ All {len(durations)} requests met SLA of {timeout:.1f}s")
    
    if failed:
        print("Failed Requests:")
        for i, r in enumerate(failed, 1):
            print(f"  {i}. {r['error']} (duration: {r['duration']:.3f}s)")
    
    return {
        "scenario": scenario_name,
        "total": len(results),
        "successful": len(successful),
        "failed": len(failed),
        "success_rate": len(successful) / len(results) if results else 0,
        "durations": [r["duration"] for r in successful] if successful else [],
    }


async def main():
    """Run all load tests."""
    import sys
    import os
    
    # Get configuration from environment
    token = os.getenv("SPRINTFLOW_TOKEN") or sys.argv[1] if len(sys.argv) > 1 else None
    project_id = int(os.getenv("SPRINTFLOW_PROJECT_ID", "1"))
    base_url = os.getenv("SPRINTFLOW_BASE_URL", "http://localhost:8000")
    
    if not token:
        print("ERROR: Must provide SPRINTFLOW_TOKEN environment variable or as argument")
        print("Usage: python load_test.py <token> [base_url] [project_id]")
        sys.exit(1)
    
    LoadTestConfig.BASE_URL = base_url
    LoadTestConfig.BEARER_TOKEN = token
    LoadTestConfig.PROJECT_ID = project_id
    
    print("=" * 80)
    print("GitLab Integration Load Test")
    print("=" * 80)
    print(f"Base URL: {base_url}")
    print(f"Project ID: {project_id}")
    print(f"Started: {datetime.now().isoformat()}")
    print()
    
    # Run all scenarios
    all_results = []
    for scenario_name, config in LoadTestConfig.SCENARIOS.items():
        result = await run_load_test(scenario_name, config, token, project_id)
        all_results.append(result)
    
    # Summary
    print("\n" + "=" * 80)
    print("Load Test Summary")
    print("=" * 80)
    print()
    print("Scenario".ljust(20), "Requests".rjust(10), "Success Rate".rjust(15), "Avg Time".rjust(12))
    print("-" * 80)
    
    for result in all_results:
        scenario = result["scenario"]
        total = result["total"]
        success_rate = f"{result['success_rate']*100:.0f}%"
        avg_time = statistics.mean(result["durations"]) if result["durations"] else 0
        avg_str = f"{avg_time:.3f}s"
        
        print(scenario.ljust(20), str(total).rjust(10), success_rate.rjust(15), avg_str.rjust(12))
    
    print()
    
    # Overall assessment
    total_requests = sum(r["total"] for r in all_results)
    total_successful = sum(r["successful"] for r in all_results)
    total_rate = total_successful / total_requests if total_requests else 0
    
    print(f"Total Requests: {total_requests}")
    print(f"Total Successful: {total_successful}")
    print(f"Overall Success Rate: {total_rate*100:.1f}%")
    print()
    
    # SLA assessment
    all_durations = []
    for result in all_results:
        all_durations.extend(result["durations"])
    
    if all_durations:
        avg_all = statistics.mean(all_durations)
        p95 = sorted(all_durations)[int(len(all_durations) * 0.95)]
        
        print(f"Overall Average Response Time: {avg_all:.3f}s")
        print(f"95th Percentile Response Time: {p95:.3f}s")
        print()
        
        # Pass/fail
        if avg_all < 0.5 and p95 < 1.0 and total_rate > 0.99:
            print("✓ LOAD TEST PASSED - All SLAs met")
            sys.exit(0)
        else:
            print("✗ LOAD TEST FAILED - Some SLAs not met")
            print("  Recommendations:")
            if avg_all > 0.5:
                print("    - Add database indexes")
                print("    - Implement caching for metrics")
            if p95 > 1.0:
                print("    - Optimize query performance")
                print("    - Consider Redis caching")
            if total_rate < 0.99:
                print("    - Check for database connection issues")
                print("    - Investigate timeout settings")
            sys.exit(1)
    else:
        print("✗ No successful requests - Cannot evaluate SLAs")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
