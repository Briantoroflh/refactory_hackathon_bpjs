"""
Team and organization management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.databases import get_db
from app.services.schemas import TeamResponse, WorkerResponse
from app.controllers.teams import (
    add_team_member as controller_add_team_member,
    create_category as controller_create_category,
    create_division as controller_create_division,
    create_team as controller_create_team,
    get_my_teams as controller_get_my_teams,
    get_team as controller_get_team,
    get_team_members as controller_get_team_members,
    list_categories as controller_list_categories,
    list_divisions as controller_list_divisions,
    list_teams as controller_list_teams,
    remove_team_member as controller_remove_team_member,
    update_team as controller_update_team,
)

router = APIRouter(prefix="/teams", tags=["teams"])


from app.routes.dependencies import require_auth



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
    return await controller_create_team(name, category_id, description, capacity_hours, db)


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
    return await controller_list_teams(db, skip, limit, category_id, status)


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """Get team by ID"""
    return await controller_get_team(team_id, db)


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
    return await controller_update_team(team_id, name, description, capacity_hours, status, db)


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
    return await controller_add_team_member(team_id, worker_id, role, db)


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
    return await controller_remove_team_member(team_id, member_id, db)


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
    return await controller_get_team_members(team_id, db)


@router.get("/my-teams")
async def get_my_teams(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """
    Get teams that current user is a member of
    
    TODO: Filter by current user from JWT token
    """
    return await controller_get_my_teams()


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
    return await controller_create_division(name, description, db)


@divisions_router.get("")
async def list_divisions(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_auth),
):
    """List all divisions"""
    return await controller_list_divisions(db)


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
    return await controller_create_category(name, division_id, description, db)


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
    return await controller_list_categories(db, division_id)
