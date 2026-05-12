"""
Team and organization management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from typing import List, Optional
from app.models import Team, TeamMember, TeamWorkspace, Division, Category, Worker
from app.databases import get_db
from app.services.schemas import TeamResponse, WorkerResponse
from datetime import datetime, timezone

router = APIRouter(prefix="/teams", tags=["teams"])


async def require_auth():
    """Dependency to check authentication - TODO: Implement token validation"""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )


@router.post("", response_model=TeamResponse)
async def create_team(
    name: str = Query(...),
    category_id: int = Query(...),
    description: Optional[str] = Query(None),
    capacity_hours: float = Query(160),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Create a new team
    
    - **name**: Team name
    - **category_id**: Category/Department ID
    - **description**: Team description
    - **capacity_hours**: Team capacity (default 160 hours)
    """
    # Verify category exists
    stmt = select(Category).where(Category.category_id == category_id)
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    team = Team(
        name=name,
        category_id=category_id,
        description=description,
        capacity_hours=capacity_hours,
        status="active",
    )
    
    db.add(team)
    await db.commit()
    await db.refresh(team)
    
    return team


@router.get("", response_model=List[TeamResponse])
async def list_teams(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    status: Optional[str] = None,
):
    """
    List teams with pagination and filtering
    
    - **skip**: Pagination offset
    - **limit**: Max records (1-100)
    - **category_id**: Filter by category
    - **status**: Filter by status (active, inactive, archived)
    """
    stmt = select(Team)
    
    if category_id:
        stmt = stmt.where(Team.category_id == category_id)
    if status:
        stmt = stmt.where(Team.status == status)
    
    stmt = stmt.offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    teams = result.scalars().all()
    
    return teams


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """Get team by ID"""
    stmt = select(Team).where(Team.team_id == team_id)
    result = await db.execute(stmt)
    team = result.scalar_one_or_none()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    return team


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int,
    name: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    capacity_hours: Optional[float] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Update team information
    
    - **team_id**: Team ID
    - **name**: New name
    - **description**: New description
    - **capacity_hours**: New capacity
    - **status**: New status
    """
    stmt = select(Team).where(Team.team_id == team_id)
    result = await db.execute(stmt)
    team = result.scalar_one_or_none()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    if name:
        team.name = name
    if description is not None:
        team.description = description
    if capacity_hours:
        team.capacity_hours = capacity_hours
    if status:
        team.status = status
    
    team.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(team)
    
    return team


@router.post("/{team_id}/members")
async def add_team_member(
    team_id: int,
    worker_id: int = Query(...),
    role: str = Query("member"),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Add member to team
    
    - **team_id**: Team ID
    - **worker_id**: Worker ID to add
    - **role**: Member role (e.g., 'member', 'lead', 'manager')
    """
    # Verify team exists
    stmt = select(Team).where(Team.team_id == team_id)
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Verify worker exists
    stmt = select(Worker).where(Worker.worker_id == worker_id)
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worker not found"
        )
    
    # Check if already member
    stmt = select(TeamMember).where(
        and_(TeamMember.team_id == team_id, TeamMember.worker_id == worker_id)
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Worker is already a member of this team"
        )
    
    member = TeamMember(
        team_id=team_id,
        worker_id=worker_id,
        role=role,
        join_date=datetime.now(timezone.utc),
    )
    
    db.add(member)
    await db.commit()
    
    return {"message": "Member added to team successfully"}


@router.delete("/{team_id}/members/{member_id}")
async def remove_team_member(
    team_id: int,
    member_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Remove member from team
    
    - **team_id**: Team ID
    - **member_id**: Team member ID to remove
    """
    stmt = select(TeamMember).where(
        and_(TeamMember.team_member_id == member_id, TeamMember.team_id == team_id)
    )
    result = await db.execute(stmt)
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )
    
    await db.delete(member)
    await db.commit()
    
    return {"message": "Member removed from team successfully"}


@router.get("/{team_id}/members")
async def get_team_members(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Get all members of a team
    
    - **team_id**: Team ID
    """
    stmt = select(TeamMember).where(TeamMember.team_id == team_id)
    result = await db.execute(stmt)
    members = result.scalars().all()
    
    return {"team_id": team_id, "members": members}


@router.get("/my-teams")
async def get_my_teams(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Get teams that current user is a member of
    
    TODO: Filter by current user from JWT token
    """
    # Placeholder - needs current user context
    return {"teams": []}


# Division endpoints
divisions_router = APIRouter(prefix="/divisions", tags=["divisions"])


@divisions_router.post("")
async def create_division(
    name: str = Query(...),
    description: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Create a new division (admin only)
    
    - **name**: Division name
    - **description**: Division description
    """
    # Check for duplicate
    stmt = select(Division).where(Division.name == name)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Division with this name already exists"
        )
    
    division = Division(name=name, description=description)
    db.add(division)
    await db.commit()
    await db.refresh(division)
    
    return division


@divisions_router.get("")
async def list_divisions(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """List all divisions"""
    stmt = select(Division)
    result = await db.execute(stmt)
    divisions = result.scalars().all()
    
    return divisions


# Category endpoints
categories_router = APIRouter(prefix="/categories", tags=["categories"])


@categories_router.post("")
async def create_category(
    name: str = Query(...),
    division_id: int = Query(...),
    description: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Create a new category (admin only)
    
    - **name**: Category name
    - **division_id**: Parent division ID
    - **description**: Category description
    """
    # Verify division exists
    stmt = select(Division).where(Division.division_id == division_id)
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Division not found"
        )
    
    category = Category(
        name=name,
        division_id=division_id,
        description=description,
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    
    return category


@categories_router.get("")
async def list_categories(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
    division_id: Optional[int] = None,
):
    """
    List categories
    
    - **division_id**: Filter by division (optional)
    """
    stmt = select(Category)
    
    if division_id:
        stmt = stmt.where(Category.division_id == division_id)
    
    result = await db.execute(stmt)
    categories = result.scalars().all()
    
    return categories
