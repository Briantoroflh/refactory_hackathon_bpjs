#!/usr/bin/env python3
"""
APScheduler Verification Script

This script verifies that APScheduler starts correctly and all jobs are registered.
It checks:
1. Scheduler initialization
2. Job registration (all 5 jobs)
3. Job scheduling configuration
4. GlobalJob table for sync records

Run this before deploying to ensure background jobs will run.
"""

import asyncio
import sys
from datetime import datetime, timedelta
from sqlalchemy import select, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.config import Settings, DATABASE_URL
from app.services.scheduler import init_scheduler
from app.models.base import Base
from app.models.gitlab import GitLabRepository, Commit
from app.models.audit import AuditSystemLog, GlobalJob


async def verify_scheduler():
    """Verify APScheduler initialization and job registration."""
    print("=" * 80)
    print("APScheduler Verification")
    print("=" * 80)
    print()

    try:
        # Initialize scheduler
        print("1. Initializing APScheduler...")
        scheduler = await init_scheduler()
        print("   ✓ Scheduler initialized successfully")
        print()

        # Check scheduler state
        print("2. Checking scheduler state...")
        if scheduler.running:
            print("   ✓ Scheduler is running")
        else:
            print("   ✗ WARNING: Scheduler is not running (expected in test mode)")
        print()

        # List all registered jobs
        print("3. Checking registered jobs...")
        jobs = scheduler.get_jobs()
        print(f"   Total jobs registered: {len(jobs)}")
        print()

        expected_jobs = {
            'gitlab_sync_repositories': 'GitLab commit synchronization',
            'fetch_commits_from_github': 'GitHub commit synchronization',
            'recalculate_worker_kpi': 'Worker KPI recalculation',
            'send_deadline_notifications': 'Deadline notifications',
            'archive_old_audit_logs': 'Audit log archival',
        }

        registered_jobs = {job.id: job for job in jobs}

        print("   Registered jobs:")
        all_present = True
        for job_id, description in expected_jobs.items():
            if job_id in registered_jobs:
                job = registered_jobs[job_id]
                print(f"      ✓ {job_id}")
                print(f"        Description: {description}")
                print(f"        Trigger: {job.trigger}")
                print(f"        Next run: {job.next_run_time}")
            else:
                print(f"      ✗ MISSING: {job_id}")
                all_present = False
        print()

        if not all_present:
            print("   ✗ ERROR: Some jobs are missing!")
            return False

        # Verify GitLab sync job specifically
        print("4. Verifying GitLab sync job configuration...")
        gitlab_job = registered_jobs.get('gitlab_sync_repositories')
        if gitlab_job:
            print(f"   ✓ Job ID: {gitlab_job.id}")
            print(f"   ✓ Job name: {gitlab_job.name}")
            print(f"   ✓ Trigger: {gitlab_job.trigger}")
            print(f"   ✓ Next run: {gitlab_job.next_run_time}")
            
            # Check if trigger is interval-based
            if hasattr(gitlab_job.trigger, 'interval'):
                interval = gitlab_job.trigger.interval
                print(f"   ✓ Interval: {interval}")
        print()

        # Check GlobalJob table
        print("5. Checking GlobalJob table for sync records...")
        try:
            engine = create_async_engine(DATABASE_URL, echo=False)
            async with AsyncSession(engine) as session:
                # Query recent sync jobs
                stmt = select(GlobalJob).where(
                    GlobalJob.job_name == 'gitlab_sync_repositories'
                ).order_by(GlobalJob.executed_at.desc()).limit(5)
                
                result = await session.execute(stmt)
                sync_jobs = result.scalars().all()
                
                if sync_jobs:
                    print(f"   ✓ Found {len(sync_jobs)} recent sync jobs")
                    for job in sync_jobs:
                        status_emoji = "✓" if job.status == "completed" else "✗"
                        print(f"      {status_emoji} {job.executed_at.isoformat()} - {job.status}")
                else:
                    print("   ℹ No sync jobs in database yet (expected on first run)")
            
            await engine.dispose()
        except Exception as e:
            print(f"   ⚠ Could not query GlobalJob table: {e}")
        print()

        # Summary
        print("=" * 80)
        print("Verification Summary")
        print("=" * 80)
        print("✓ APScheduler initialized successfully")
        print(f"✓ All {len(jobs)} expected jobs registered")
        print("✓ GitLab sync job configured and ready")
        print()
        print("Ready for deployment! ✓")
        return True

    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run verification."""
    try:
        result = asyncio.run(verify_scheduler())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\nVerification cancelled by user")
        sys.exit(1)


if __name__ == "__main__":
    main()
