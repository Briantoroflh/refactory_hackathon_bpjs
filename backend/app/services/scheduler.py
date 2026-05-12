"""
Background job scheduler setup using APScheduler
If APScheduler is not installed, scheduler functions become no-ops and a warning is logged.
"""
try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger
    APSCHEDULER_AVAILABLE = True
except Exception:  # pragma: no cover - defensive
    AsyncIOScheduler = None
    CronTrigger = None
    APSCHEDULER_AVAILABLE = False
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
import asyncio
import logging

from app.config import get_settings
from app.models import (
    ProjectCommitTracking,
    WorkerKPI,
    ProjectTask,
    GlobalJob,
    Project,
)

logger = logging.getLogger(__name__)

scheduler = None


async def get_async_session():
    """Get async database session for background jobs"""
    settings = get_settings()
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_size=10,
        max_overflow=20,
    )
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    return async_session()


async def fetch_commits_from_github(project_id: int):
    """
    Background job: Fetch commits from GitHub/GitLab for a project
    
    This job:
    1. Retrieves repository URL and token from project
    2. Calls GitHub/GitLab API to fetch recent commits
    3. Stores new commits in database
    4. Updates last sync timestamp
    """
    try:
        db = await get_async_session()
        
        # TODO: Implement GitHub/GitLab API integration
        # 1. Get project with repository details
        # 2. Call API to fetch commits
        # 3. Store in ProjectCommitTracking table
        # 4. Log job execution
        
        job_log = GlobalJob(
            job_name="fetch_commits_from_github",
            resource_id=project_id,
            status="completed",
            executed_at=datetime.now(timezone.utc),
            details="Commit fetch job executed"
        )
        db.add(job_log)
        await db.commit()
        
        logger.info(f"Commit fetch job completed for project {project_id}")
        
    except Exception as e:
        logger.error(f"Commit fetch job failed for project {project_id}: {str(e)}")


async def recalculate_worker_kpi():
    """
    Background job: Recalculate worker KPI scores
    
    This job:
    1. Finds all completed projects
    2. Calculates KPI metrics for each worker
    3. Updates WorkerKPI scores
    4. Logs results
    """
    try:
        db = await get_async_session()
        
        # TODO: Implement KPI calculation logic
        # 1. Get all completed projects
        # 2. Calculate KPI for each worker on project
        # 3. Update WorkerKPI table
        # 4. Log job execution
        
        job_log = GlobalJob(
            job_name="recalculate_worker_kpi",
            status="completed",
            executed_at=datetime.now(timezone.utc),
            details="KPI recalculation job executed"
        )
        db.add(job_log)
        await db.commit()
        
        logger.info("KPI recalculation job completed")
        
    except Exception as e:
        logger.error(f"KPI recalculation job failed: {str(e)}")


async def send_deadline_notifications():
    """
    Background job: Send notifications for approaching deadlines
    
    This job:
    1. Finds tasks with deadlines in next 3 days
    2. Sends notifications to assigned users
    3. Logs notification delivery
    """
    try:
        db = await get_async_session()
        
        # TODO: Implement notification sending
        # 1. Query ProjectTask where deadline is within 3 days
        # 2. Send email/in-app notifications
        # 3. Update notification status
        # 4. Log job execution
        
        job_log = GlobalJob(
            job_name="send_deadline_notifications",
            status="completed",
            executed_at=datetime.now(timezone.utc),
            details="Deadline notification job executed"
        )
        db.add(job_log)
        await db.commit()
        
        logger.info("Deadline notification job completed")
        
    except Exception as e:
        logger.error(f"Deadline notification job failed: {str(e)}")


async def archive_old_audit_logs():
    """
    Background job: Archive old audit logs to cold storage
    
    This job:
    1. Finds audit logs older than 90 days
    2. Exports to archive storage
    3. Deletes from active database
    4. Logs archival details
    """
    try:
        db = await get_async_session()
        
        # TODO: Implement audit log archival
        # 1. Query logs older than 90 days
        # 2. Export to archive storage (S3, blob storage, etc)
        # 3. Delete from database
        # 4. Log job execution
        
        job_log = GlobalJob(
            job_name="archive_old_audit_logs",
            status="completed",
            executed_at=datetime.now(timezone.utc),
            details="Audit log archival job executed"
        )
        db.add(job_log)
        await db.commit()
        
        logger.info("Audit log archival job completed")
        
    except Exception as e:
        logger.error(f"Audit log archival job failed: {str(e)}")


async def gitlab_sync_repositories():
    """
    Background job: Synchronize commits from GitLab repositories
    
    This job:
    1. Gets all linked GitLab repositories
    2. Fetches commits since last sync
    3. Stores commits in database
    4. Updates sync timestamps
    5. Logs results to audit trail
    """
    try:
        db = await get_async_session()
        settings = get_settings()
        
        from app.services.commit_sync import CommitSyncService
        
        total_synced, total_errors, status_msg = await CommitSyncService.sync_all_repositories(
            db,
            settings.GITLAB_API_BASE_URL,
            lookback_days=90,
        )
        
        job_log = GlobalJob(
            job_name="gitlab_sync_repositories",
            status="completed" if total_errors == 0 else "completed_with_errors",
            executed_at=datetime.now(timezone.utc),
            details={
                "total_synced": total_synced,
                "total_errors": total_errors,
                "status": status_msg,
            }
        )
        db.add(job_log)
        await db.commit()
        
        logger.info(f"GitLab commit sync job completed: {status_msg}")
        
    except Exception as e:
        logger.error(f"GitLab commit sync job failed: {str(e)}")
        try:
            db = await get_async_session()
            job_log = GlobalJob(
                job_name="gitlab_sync_repositories",
                status="failed",
                executed_at=datetime.now(timezone.utc),
                details={"error": str(e)}
            )
            db.add(job_log)
            await db.commit()
        except Exception as log_error:
            logger.error(f"Failed to log GitLab sync error: {str(log_error)}")


def init_scheduler():
    """Initialize and start the job scheduler"""
    global scheduler
    if not APSCHEDULER_AVAILABLE:
        logger.warning("APScheduler not installed — background jobs disabled")
        return

    scheduler = AsyncIOScheduler()
    
    # Get settings for interval configuration
    settings = get_settings()
    
    # Schedule: Sync GitLab repositories
    gitlab_sync_interval = getattr(settings, 'GITLAB_SYNC_INTERVAL_MINUTES', 15)
    if gitlab_sync_interval > 0:
        scheduler.add_job(
            gitlab_sync_repositories,
            'interval',
            minutes=gitlab_sync_interval,
            id="gitlab_sync_job",
            name="Sync GitLab repositories",
            replace_existing=True,
        )
        logger.info(f"GitLab sync job scheduled every {gitlab_sync_interval} minutes")
    
    # Schedule: Fetch commits from GitHub every 6 hours
    scheduler.add_job(
        fetch_commits_from_github,
        CronTrigger(hour="*/6"),
        id="fetch_commits_job",
        name="Fetch commits from GitHub",
        replace_existing=True,
        args=[1]  # TODO: Make this dynamic per project
    )
    
    # Schedule: Recalculate KPI daily at 2 AM
    scheduler.add_job(
        recalculate_worker_kpi,
        CronTrigger(hour=2, minute=0),
        id="recalculate_kpi_job",
        name="Recalculate worker KPI",
        replace_existing=True,
    )
    
    # Schedule: Send deadline notifications daily at 8 AM
    scheduler.add_job(
        send_deadline_notifications,
        CronTrigger(hour=8, minute=0),
        id="deadline_notifications_job",
        name="Send deadline notifications",
        replace_existing=True,
    )
    
    # Schedule: Archive old audit logs weekly on Sunday at 3 AM
    scheduler.add_job(
        archive_old_audit_logs,
        CronTrigger(day_of_week=6, hour=3, minute=0),
        id="archive_logs_job",
        name="Archive old audit logs",
        replace_existing=True,
    )
    
    logger.info("Background job scheduler initialized with 5 jobs")


async def start_scheduler():
    """Start the background job scheduler"""
    global scheduler
    if not APSCHEDULER_AVAILABLE:
        logger.debug("start_scheduler called but APScheduler is not available")
        return

    if scheduler is None:
        init_scheduler()

    if scheduler and not scheduler.running:
        scheduler.start()
        logger.info("Background job scheduler started")


async def stop_scheduler():
    """Stop the background job scheduler"""
    global scheduler
    if not APSCHEDULER_AVAILABLE:
        logger.debug("stop_scheduler called but APScheduler is not available")
        return

    if scheduler and scheduler.running:
        scheduler.shutdown()
        logger.info("Background job scheduler stopped")
