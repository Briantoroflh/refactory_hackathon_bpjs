"""Project management routes."""

from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.projects import (
    create_project as controller_create_project,
    get_project as controller_get_project,
    get_project_details as controller_get_project_details,
    get_project_teams as controller_get_project_teams,
    list_projects as controller_list_projects,
    list_workspace_projects as controller_list_workspace_projects,
    link_repository as controller_link_repository,
    update_project as controller_update_project,
    update_project_status as controller_update_project_status,
)
from app.databases import get_db
from app.models import Project, ProjectTask, ProjectTeam, ProjectTeamMember, ProjectWorkspace, User, Worker, WorkerKPI
from app.models.gitlab import Commit, GitLabRepository
from app.services.schemas import (
    ProjectCreateRequest,
    ProjectResponse,
    ProjectStatusUpdateRequest,
    ProjectUpdateRequest,
)

router = APIRouter(prefix="/projects", tags=["projects"])


from app.routes.dependencies import require_auth



@router.post("", response_model=ProjectResponse)
async def create_project(
    req: ProjectCreateRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Create a new project
    
    - **name**: Project name (required)
    - **description**: Project description (optional)
    - **workspace_id**: Workspace ID (required)
    - **team_ids**: List of team IDs to associate (optional)
    """
    return await controller_create_project(req, db)


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    workspace_id: Optional[int] = None,
):
    """
    List projects with pagination and filtering
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Number of records to return (max 100)
    - **status**: Filter by status (planning, active, completed, archived)
    - **workspace_id**: Filter by workspace ID
    """
    return await controller_list_projects(db, skip, limit, status, workspace_id)


@router.get("/overview", summary="Get live project overview", response_model=dict)
async def get_projects_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
    days: int = Query(7, ge=1, le=30),
):
    now = datetime.utcnow()
    current_window_start = now - timedelta(days=days)
    previous_window_start = now - timedelta(days=days * 2)

    projects_result = await db.execute(select(Project).order_by(Project.updated_at.desc()))
    projects = projects_result.scalars().all()

    if not projects:
        return {"projects": [], "repositories": []}

    project_ids = [project.project_id for project in projects]

    repo_result = await db.execute(
        select(GitLabRepository, Project)
        .join(Project, Project.project_id == GitLabRepository.project_id)
        .where(GitLabRepository.project_id.in_(project_ids))
    )
    repo_rows = repo_result.all()
    repo_by_project = {project.project_id: repository for repository, project in repo_rows}

    task_result = await db.execute(
        select(
            ProjectTask.project_id,
            func.count(ProjectTask.task_id).label("total"),
            func.sum(case((ProjectTask.status.in_(["completed", "closed"]), 1), else_=0)).label("completed"),
            func.sum(case((ProjectTask.priority == "high", 1), else_=0)).label("high_priority"),
        )
        .where(ProjectTask.project_id.in_(project_ids))
        .group_by(ProjectTask.project_id)
    )
    task_stats = {
        row.project_id: {
            "total": int(row.total or 0),
            "completed": int(row.completed or 0),
            "high_priority": int(row.high_priority or 0),
        }
        for row in task_result.all()
    }

    members_result = await db.execute(
        select(
            ProjectTeam.project_id,
            Worker.worker_id,
            Worker.full_name,
            Worker.email,
        )
        .join(ProjectTeamMember, ProjectTeamMember.project_team_id == ProjectTeam.project_team_id)
        .join(Worker, Worker.worker_id == ProjectTeamMember.worker_id)
        .where(ProjectTeam.project_id.in_(project_ids))
        .order_by(ProjectTeam.project_id, Worker.full_name)
    )
    members_by_project = defaultdict(list)
    for row in members_result.all():
        members_by_project[row.project_id].append(
            {
                "id": str(row.worker_id),
                "name": row.full_name,
                "avatar": "".join(part[0] for part in row.full_name.split()[:2]).upper() or row.email[:2].upper(),
            }
        )

    current_commit_result = await db.execute(
        select(
            GitLabRepository.project_id,
            func.count(Commit.id).label("count"),
        )
        .join(Commit, Commit.repository_id == GitLabRepository.id)
        .where(Commit.committed_at >= current_window_start)
        .group_by(GitLabRepository.project_id)
    )
    current_commits = {row.project_id: int(row.count or 0) for row in current_commit_result.all()}

    previous_commit_result = await db.execute(
        select(
            GitLabRepository.project_id,
            func.count(Commit.id).label("count"),
        )
        .join(Commit, Commit.repository_id == GitLabRepository.id)
        .where(
            Commit.committed_at >= previous_window_start,
            Commit.committed_at < current_window_start,
        )
        .group_by(GitLabRepository.project_id)
    )
    previous_commits = {row.project_id: int(row.count or 0) for row in previous_commit_result.all()}

    bar_result = await db.execute(
        select(
            GitLabRepository.project_id,
            func.date(Commit.committed_at).label("day"),
            func.count(Commit.id).label("count"),
        )
        .join(Commit, Commit.repository_id == GitLabRepository.id)
        .where(Commit.committed_at >= current_window_start)
        .group_by(GitLabRepository.project_id, func.date(Commit.committed_at))
    )
    bars_by_project = defaultdict(dict)
    for row in bar_result.all():
        if row.day:
            bars_by_project[row.project_id][row.day] = int(row.count or 0)

    def _relative_label(updated_at: datetime | None) -> str:
        if not updated_at:
            return "Just now"
        delta = now - updated_at
        seconds = int(delta.total_seconds())
        if seconds < 60:
            return "Just now"
        minutes = seconds // 60
        if minutes < 60:
            return f"{minutes}m ago"
        hours = minutes // 60
        if hours < 24:
            return f"{hours}h ago"
        days_ago = hours // 24
        return f"{days_ago}d ago"

    def _platform_label(project: Project) -> str:
        value = (project.repository_type or "").lower()
        if value == "gitlab":
            return "GitLab"
        if value == "bitbucket":
            return "GitHub"
        if value == "github" or not value:
            return "GitHub"
        return project.repository_type.capitalize()

    def _health_score(progress: int, commits: int, blockers: int, member_count: int) -> int:
        commit_score = min(commits * 8, 100)
        team_score = 100 if member_count else 40
        blocker_penalty = min(blockers * 12, 48)
        score = round((progress * 0.45) + (commit_score * 0.3) + (team_score * 0.25) - blocker_penalty)
        return max(0, min(score, 100))

    def _project_status(score: int, blockers: int) -> str:
        if score >= 85 and blockers == 0:
            return "healthy"
        if score >= 70:
            return "warning"
        return "critical"

    def _health_delta(current: int, previous: int) -> int:
        if previous <= 0:
            return current
        return int(round(((current - previous) / previous) * 100))

    def _commit_bars(project_id: int) -> list[int]:
        counts = bars_by_project.get(project_id, {})
        bars = []
        for offset in range(days - 1, -1, -1):
            day = (now.date() - timedelta(days=offset)).isoformat()
            bars.append(int(counts.get(day, 0)))
        return bars

    def _project_name_from_repo(project: Project) -> str:
        if project.repository_url:
            slug = project.repository_url.rstrip("/").split("/")[-1]
            return slug.removesuffix(".git") or project.name
        return project.name

    projects_payload = []
    repositories_payload = []
    for project in projects:
        stats = task_stats.get(project.project_id, {"total": 0, "completed": 0, "high_priority": 0})
        total_tasks = stats["total"]
        completed_tasks = stats["completed"]
        blockers = stats["high_priority"]
        progress = int(round((completed_tasks / total_tasks) * 100)) if total_tasks else 0
        current_commits_count = current_commits.get(project.project_id, 0)
        previous_commits_count = previous_commits.get(project.project_id, 0)
        score = _health_score(progress, current_commits_count, blockers, len(members_by_project.get(project.project_id, [])))
        repository = repo_by_project.get(project.project_id)

        projects_payload.append(
            {
                "id": str(project.project_id),
                "name": project.name,
                "platform": _platform_label(project),
                "description": project.description or "No description available.",
                "status": _project_status(score, blockers),
                "aiHealthScore": score,
                "healthDelta": _health_delta(current_commits_count, previous_commits_count),
                "commitVelocity": current_commits_count,
                "commitBars": _commit_bars(project.project_id),
                "progress": progress,
                "updatedAtLabel": _relative_label(project.updated_at),
                "members": members_by_project.get(project.project_id, [])[:3],
            }
        )

        if repository:
            last_sync = repository.last_sync_timestamp
            if last_sync and (now - last_sync) <= timedelta(hours=24):
                repo_status = "syncing"
            elif last_sync and (now - last_sync) <= timedelta(days=7):
                repo_status = "paused"
            else:
                repo_status = "failed"

            repositories_payload.append(
                {
                    "id": str(repository.id),
                    "repositoryName": _project_name_from_repo(project),
                    "platform": _platform_label(project),
                    "status": repo_status,
                }
            )

    return {
        "projects": projects_payload,
        "repositories": repositories_payload,
        "generatedAt": now.isoformat(),
        "requestedBy": current_user.user_id,
    }


@router.get("/{project_id}/sprint-overview", summary="Get live sprint overview", response_model=dict)
async def get_project_sprint_overview(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    now = datetime.utcnow()
    project_result = await db.execute(select(Project).where(Project.project_id == project_id))
    project = project_result.scalars().first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    workspace_result = await db.execute(
        select(ProjectWorkspace).where(ProjectWorkspace.workspace_id == project.workspace_id)
    )
    workspace = workspace_result.scalars().first()

    tasks_result = await db.execute(select(ProjectTask).where(ProjectTask.project_id == project_id))
    tasks = tasks_result.scalars().all()

    project_team_result = await db.execute(
        select(ProjectTeam.project_team_id).where(ProjectTeam.project_id == project_id)
    )
    project_team_ids = [row.project_team_id for row in project_team_result.all()]

    members_payload = []
    if project_team_ids:
        member_result = await db.execute(
            select(Worker.worker_id, Worker.full_name, Worker.email, ProjectTeamMember.role)
            .join(Worker, Worker.worker_id == ProjectTeamMember.worker_id)
            .where(ProjectTeamMember.project_team_id.in_(project_team_ids))
            .order_by(Worker.full_name)
        )
        palette = ["#4f46e5", "#0891b2", "#f97316", "#2563eb", "#10b981", "#8b5cf6"]
        for index, row in enumerate(member_result.all()):
            initials = "".join(part[0] for part in row.full_name.split()[:2]).upper() or row.email[:2].upper()
            members_payload.append(
                {
                    "id": str(row.worker_id),
                    "name": row.full_name,
                    "avatar": initials,
                    "color": palette[index % len(palette)],
                }
            )

    completed_statuses = {"completed", "closed"}
    active_statuses = {"backlog", "in_progress", "in_review"}
    total_points = sum(task.story_points or 0 for task in tasks)
    completed_points = sum(task.story_points or 0 for task in tasks if task.status in completed_statuses)
    remaining_points = max(total_points - completed_points, 0)
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.status in completed_statuses)
    active_tasks = sum(1 for task in tasks if task.status in active_statuses)
    blockers = sum(1 for task in tasks if task.priority == "high" and task.status in active_statuses)

    def _task_status_to_sprint(status: str) -> str:
        return {
            "backlog": "todo",
            "in_progress": "in_progress",
            "in_review": "review",
            "completed": "done",
            "closed": "done",
        }.get(status, "todo")

    def _due_date_label(deadline: str | None) -> str:
        if not deadline:
            return ""
        try:
            due = datetime.fromisoformat(deadline).date()
        except ValueError:
            return deadline
        diff = (due - date.today()).days
        if diff < 0:
            return "Overdue"
        if diff == 0:
            return "Due today"
        return f"Due in {diff}d"

    sprint_end = None
    if project.end_date:
        try:
            sprint_end = datetime.fromisoformat(project.end_date).date()
        except ValueError:
            sprint_end = None

    sprint_start = None
    if project.start_date:
        try:
            sprint_start = datetime.fromisoformat(project.start_date).date()
        except ValueError:
            sprint_start = None

    days_remaining = (sprint_end - date.today()).days if sprint_end else 0

    task_payload = []
    for task in tasks:
        task_payload.append(
            {
                "id": str(task.task_id),
                "title": task.title,
                "status": _task_status_to_sprint(task.status),
                "priority": task.priority,
                "dueDate": task.deadline or "",
                "storyPoints": task.story_points or 0,
                "tags": [task.priority.capitalize()] if task.priority else ["General"],
                "assigneeIds": [str(task.assigned_to)] if task.assigned_to else [],
                "version": task.version,
            }
        )

    weekly_buckets: dict[str, int] = {}
    for offset in range(3, -1, -1):
        week_start = date.today() - timedelta(days=offset * 7)
        label = f"S{week_start.isocalendar().week}"
        weekly_buckets[label] = 0

    for task in tasks:
        if task.status not in completed_statuses or not task.updated_at:
            continue
        updated_date = task.updated_at.date() if hasattr(task.updated_at, "date") else task.updated_at
        week_key = f"S{updated_date.isocalendar().week}"
        if week_key in weekly_buckets:
            weekly_buckets[week_key] += task.story_points or 0

    velocity = [{"label": label, "value": value} for label, value in weekly_buckets.items()]

    summary = {
        "id": f"project-{project.project_id}-sprint",
        "name": f"{project.name} Active Sprint",
        "projectPath": [
            "Sprints",
            workspace.name if workspace else project.name,
            project.name,
        ],
        "startDateLabel": sprint_start.strftime("%b %d") if sprint_start else "Not set",
        "endDateLabel": sprint_end.strftime("%b %d") if sprint_end else "Not set",
        "daysRemaining": max(days_remaining, 0),
        "storyPointGoal": total_points,
    }

    progress = int(round((completed_points / total_points) * 100)) if total_points else 0
    insight_status = "on track" if blockers == 0 and progress >= 60 else "at risk"
    insight_alert_title = "Review Delay Detected" if active_tasks else "No Active Work"
    insight_alert_body = (
        f"{blockers} high-priority tasks need attention."
        if blockers
        else "No active blockers in the sprint right now."
    )

    return {
        "sprint": summary,
        "members": members_payload,
        "stats": [
            {"id": "total", "label": "Total Points", "value": str(total_points)},
            {"id": "completed", "label": "Completed", "value": str(completed_points), "tone": "success"},
            {"id": "remaining", "label": "Remaining", "value": str(remaining_points), "tone": "warning"},
        ],
        "tasks": task_payload,
        "velocity": velocity,
        "insights": {
            "title": "AI Standup Insight",
            "subtitle": "Synthesized from live sprint data",
            "summary": f"The team is currently {insight_status} to meet sprint goals.",
            "alertTitle": insight_alert_title,
            "alertBody": insight_alert_body,
            "status": "on_track" if insight_status == "on track" else "at_risk",
        },
        "generatedAt": now.isoformat(),
        "requestedBy": current_user.user_id,
    }


@router.get("/{project_id}/analytics-overview", summary="Get live analytics overview", response_model=dict)
async def get_project_analytics_overview(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    now = datetime.utcnow()
    project_result = await db.execute(select(Project).where(Project.project_id == project_id))
    project = project_result.scalars().first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    member_result = await db.execute(
        select(
            Worker.worker_id,
            Worker.full_name,
            Worker.email,
            ProjectTeamMember.role,
            ProjectTeamMember.allocation_percentage,
        )
        .join(ProjectTeamMember, ProjectTeamMember.worker_id == Worker.worker_id)
        .join(ProjectTeam, ProjectTeam.project_team_id == ProjectTeamMember.project_team_id)
        .where(ProjectTeam.project_id == project_id)
        .order_by(Worker.full_name)
    )

    members: dict[int, dict[str, object]] = {}
    allocations: dict[int, float] = {}
    for row in member_result.all():
        worker_id = int(row.worker_id)
        members[worker_id] = {
            "id": str(worker_id),
            "name": row.full_name,
            "role": (row.role or "engineer").replace("_", " ").title(),
            "avatar": "".join(part[0] for part in row.full_name.split()[:2]).upper() or row.email[:2].upper(),
        }
        allocations[worker_id] = allocations.get(worker_id, 0) + float(row.allocation_percentage or 0)

    kpi_result = await db.execute(
        select(
            WorkerKPI.worker_id,
            func.avg(WorkerKPI.score).label("average_score"),
        )
        .where(WorkerKPI.project_id == project_id)
        .group_by(WorkerKPI.worker_id)
    )
    quality_by_worker = {
        int(row.worker_id): float(row.average_score or 0)
        for row in kpi_result.all()
    }

    task_result = await db.execute(
        select(
            ProjectTask.assigned_to,
            ProjectTask.story_points,
            ProjectTask.status,
            ProjectTask.updated_at,
        ).where(ProjectTask.project_id == project_id)
    )
    current_window_start = now - timedelta(days=30)
    previous_window_start = now - timedelta(days=60)
    completed_statuses = {"completed", "closed"}
    current_points = 0
    previous_points = 0
    points_by_worker: dict[int, int] = defaultdict(int)
    previous_points_by_worker: dict[int, int] = defaultdict(int)

    for row in task_result.all():
        if row.status not in completed_statuses:
            continue

        completed_at = row.updated_at or now
        points = int(row.story_points or 0)

        if completed_at >= current_window_start:
            current_points += points
            if row.assigned_to:
                points_by_worker[int(row.assigned_to)] += points
        elif completed_at >= previous_window_start:
            previous_points += points
            if row.assigned_to:
                previous_points_by_worker[int(row.assigned_to)] += points

    total_allocation = sum(allocations.values()) or 0
    total_current_points = sum(points_by_worker.values()) or 0
    average_quality = round(
        sum(quality_by_worker.values()) / max(len(quality_by_worker), 1),
        1,
    )

    engineers_payload = []
    for worker_id, member in members.items():
        velocity = points_by_worker.get(worker_id, 0)
        quality = round(quality_by_worker.get(worker_id, 0), 1)
        score = round((quality * 0.09) + (min(velocity, 40) * 0.025), 1)
        if score >= 9:
            status_value = "optimal"
        elif score >= 8:
            status_value = "warning"
        else:
            status_value = "critical"

        engineers_payload.append(
            {
                "id": member["id"],
                "name": member["name"],
                "role": member["role"],
                "velocity": velocity,
                "quality": quality,
                "score": score,
                "status": status_value,
                "avatar": member["avatar"],
            }
        )

    engineers_payload.sort(key=lambda item: (item["score"], item["velocity"]), reverse=True)

    imbalance_insight = {
        "id": "insight-workload-imbalance",
        "title": "Workload Imbalance",
        "description": "Team workload is currently balanced across active members.",
        "severity": "info",
        "metric": None,
        "trend": "stable",
    }

    if members and total_current_points > 0 and total_allocation > 0:
        def _share(value: float, total: float) -> float:
            return value / total if total else 0

        worst_worker_id = None
        worst_gap = 0.0
        for worker_id, allocation in allocations.items():
            actual_share = _share(points_by_worker.get(worker_id, 0), total_current_points)
            expected_share = _share(allocation, total_allocation)
            gap = actual_share - expected_share
            if abs(gap) > abs(worst_gap):
                worst_gap = gap
                worst_worker_id = worker_id

        if worst_worker_id is not None and abs(worst_gap) >= 0.1:
            worker_name = members[worst_worker_id]["name"]
            imbalance_insight.update(
                {
                    "description": (
                        f"{worker_name} is currently assigned {abs(round(worst_gap * 100))}% "
                        f"{'more' if worst_gap > 0 else 'less'} capacity than optimal. "
                        "Consider redistributing tasks."
                    ),
                    "severity": "warning",
                    "metric": f"{abs(round(worst_gap * 100))}%",
                    "trend": "down" if worst_gap > 0 else "up",
                }
            )

    quality_insight = {
        "id": "insight-quality",
        "title": "Code Quality Improving",
        "description": (
            f"Team quality score averages {average_quality:.1f}% across live KPI data."
        ),
        "severity": "info" if average_quality >= 90 else "warning",
        "metric": f"{average_quality:.1f}%",
        "trend": "up" if average_quality >= 90 else "stable",
    }

    current_q = ((now.month - 1) // 3) + 1
    date_start = project.start_date or current_window_start.date().isoformat()
    date_end = project.end_date or now.date().isoformat()

    return {
        "sprintId": f"project-{project.project_id}-analytics",
        "sprintNumber": project.project_id,
        "quarter": f"Q{current_q}",
        "year": now.year,
        "teamVelocity": {
            "current": current_points,
            "previous": previous_points,
            "trend": round(((current_points - previous_points) / previous_points) * 100, 1) if previous_points else 0,
            "completedPoints": current_points,
        },
        "engineers": engineers_payload,
        "insights": [imbalance_insight, quality_insight],
        "dateRange": {
            "start": date_start,
            "end": date_end,
        },
        "generatedAt": now.isoformat(),
        "requestedBy": current_user.user_id,
    }


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Get project by ID
    
    - **project_id**: Project ID
    """
    return await controller_get_project(project_id, db)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    req: ProjectUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Update project with optimistic locking
    
    - **project_id**: Project ID
    - **name**: New project name
    - **description**: New description
    - **version**: Current version (for optimistic locking)
    """
    return await controller_update_project(project_id, req, db)


@router.patch("/{project_id}/status", response_model=ProjectResponse)
async def update_project_status(
    project_id: int,
    req: ProjectStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Update project status (planning → active → completed → archived)
    
    - **project_id**: Project ID
    - **status**: New status
    - **version**: Current version for optimistic locking
    """
    return await controller_update_project_status(project_id, req, db)


@router.post("/{project_id}/repository")
async def link_repository(
    project_id: int,
    repository_url: str = Query(...),
    repository_type: str = Query("github"),
    token: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Link Git repository to project
    
    - **project_id**: Project ID
    - **repository_url**: Repository URL
    - **repository_type**: Repository type (github, gitlab, bitbucket)
    - **token**: Access token (optional)
    """
    return await controller_link_repository(project_id, repository_url, repository_type, token, db)


@router.get("/{project_id}/details")
async def get_project_details(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Get extended project details
    
    - **project_id**: Project ID
    """
    return await controller_get_project_details(project_id, db)


@router.get("/{project_id}/team")
async def get_project_teams(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Get teams assigned to project
    
    - **project_id**: Project ID
    """
    return await controller_get_project_teams(project_id, db)


@router.get("")
async def list_workspace_projects(
    workspace_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Get all projects in a workspace
    
    - **workspace_id**: Workspace ID
    """
    return await controller_list_workspace_projects(workspace_id, db)
