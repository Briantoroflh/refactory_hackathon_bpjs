"""FastAPI routes for live dashboard data."""

from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.auth import get_current_user
from app.databases import get_db
from app.models import Project, ProjectTask, Team, User

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


def _format_percent_change(current: int, previous: int) -> str:
    if previous <= 0:
        return f"+{current}" if current > 0 else "0"

    change = round(((current - previous) / previous) * 100)
    return f"{change:+.0f}%"


def _make_stat(title: str, value: str, delta: str, direction: str, description: str, accent: str, icon: str) -> dict:
    return {
        "title": title,
        "value": value,
        "delta": delta,
        "deltaDirection": direction,
        "description": description,
        "accent": accent,
        "icon": icon,
    }


def _health_label(completion_rate: float, blocker_count: int) -> str:
    if completion_rate >= 80 and blocker_count == 0:
        return "Healthy"
    if completion_rate >= 55 and blocker_count <= 3:
        return "Watch"
    return "At Risk"


@router.get("/overview", summary="Get live dashboard overview", response_model=dict)
async def get_dashboard_overview(
    days: int = Query(30, ge=7, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.utcnow()
    current_window_start = now - timedelta(days=days)
    previous_window_start = now - timedelta(days=days * 2)

    total_projects = (
        await db.execute(select(func.count(Project.project_id)))
    ).scalar() or 0
    active_projects = (
        await db.execute(
            select(func.count(Project.project_id)).where(Project.status == "active")
        )
    ).scalar() or 0
    total_teams = (
        await db.execute(select(func.count(Team.team_id)))
    ).scalar() or 0
    active_teams = (
        await db.execute(select(func.count(Team.team_id)).where(Team.status == "active"))
    ).scalar() or 0

    total_tasks = (
        await db.execute(select(func.count(ProjectTask.task_id)))
    ).scalar() or 0
    completed_tasks = (
        await db.execute(
            select(func.count(ProjectTask.task_id)).where(
                ProjectTask.status.in_(["completed", "closed"])
            )
        )
    ).scalar() or 0
    blocker_count = (
        await db.execute(
            select(func.count(ProjectTask.task_id)).where(
                ProjectTask.priority == "high",
                ProjectTask.status.in_(["backlog", "in_progress", "in_review"]),
            )
        )
    ).scalar() or 0

    current_completed = (
        await db.execute(
            select(func.count(ProjectTask.task_id)).where(
                ProjectTask.status.in_(["completed", "closed"]),
                ProjectTask.updated_at >= current_window_start,
            )
        )
    ).scalar() or 0
    previous_completed = (
        await db.execute(
            select(func.count(ProjectTask.task_id)).where(
                ProjectTask.status.in_(["completed", "closed"]),
                ProjectTask.updated_at >= previous_window_start,
                ProjectTask.updated_at < current_window_start,
            )
        )
    ).scalar() or 0

    current_blockers = (
        await db.execute(
            select(func.count(ProjectTask.task_id)).where(
                ProjectTask.priority == "high",
                ProjectTask.status.in_(["backlog", "in_progress", "in_review"]),
                ProjectTask.updated_at >= current_window_start,
            )
        )
    ).scalar() or 0
    previous_blockers = (
        await db.execute(
            select(func.count(ProjectTask.task_id)).where(
                ProjectTask.priority == "high",
                ProjectTask.status.in_(["backlog", "in_progress", "in_review"]),
                ProjectTask.updated_at >= previous_window_start,
                ProjectTask.updated_at < current_window_start,
            )
        )
    ).scalar() or 0

    completion_rate = round((completed_tasks / total_tasks) * 100) if total_tasks else 0
    completion_delta = _format_percent_change(current_completed, previous_completed)
    blocker_delta = _format_percent_change(current_blockers, previous_blockers)
    team_delta = f"{active_teams}/{total_teams}" if total_teams else "0/0"

    recent_rows = await db.execute(
        select(
            func.date(ProjectTask.updated_at).label("day"),
            func.count(ProjectTask.task_id).label("count"),
        )
        .where(ProjectTask.updated_at >= (now - timedelta(days=4)))
        .group_by(func.date(ProjectTask.updated_at))
    )
    recent_counts = {row.day: row.count for row in recent_rows.all() if row.day}
    recent_bars = []
    for offset in range(4, -1, -1):
        day = (now.date() - timedelta(days=offset)).isoformat()
        recent_bars.append(
            {
                "label": date.fromisoformat(day).strftime("%a"),
                "value": int(recent_counts.get(day, 0)),
                "active": offset == 0,
            }
        )

    profile_title = (
        "Realtime overview"
        if total_projects or total_teams
        else "No live data yet"
    )
    profile_name = current_user.full_name or current_user.email

    notifications = [
        {
            "id": "notif-summary",
            "title": "Workspace summary",
            "description": f"{active_projects} of {total_projects} projects are active across {total_teams} teams.",
            "tone": "success" if active_projects else "info",
        },
        {
            "id": "notif-completion",
            "title": "Task completion",
            "description": f"{completed_tasks} tasks completed out of {total_tasks} total tasks in the live dataset.",
            "tone": "success" if completion_rate >= 70 else "warning",
        },
        {
            "id": "notif-blockers",
            "title": "Open blockers",
            "description": f"{blocker_count} high-priority tasks still need attention.",
            "tone": "warning" if blocker_count else "success",
        },
    ]

    return {
        "generatedAt": now.isoformat(),
        "profile": {
            "name": profile_name,
            "title": profile_title,
            "projects": total_projects,
            "team": total_teams,
        },
        "stats": [
            _make_stat(
                "Projects",
                str(total_projects),
                f"{active_projects} active",
                "up" if active_projects else "down",
                f"{active_projects} active projects right now",
                "from-indigo-200 to-indigo-400",
                "trend",
            ),
            _make_stat(
                "Completion Rate",
                f"{completion_rate}%",
                completion_delta,
                "up" if completion_rate >= 50 else "down",
                "Completed tasks vs total tasks",
                "from-emerald-200 to-emerald-400",
                "check",
            ),
            _make_stat(
                "Team Health",
                _health_label(completion_rate, blocker_count),
                team_delta,
                "up" if active_teams else "down",
                "Live team availability across the workspace",
                "from-amber-200 to-amber-400",
                "flame",
            ),
            _make_stat(
                "Open Blockers",
                str(blocker_count),
                blocker_delta,
                "down" if blocker_count else "up",
                "High-priority items still waiting",
                "from-rose-200 to-rose-400",
                "block",
            ),
        ],
        "sprint": {
            "title": "Active Work Progress",
            "subtitle": f"Last {days} days across live project tasks",
            "bars": recent_bars,
        },
        "notifications": notifications,
    }
