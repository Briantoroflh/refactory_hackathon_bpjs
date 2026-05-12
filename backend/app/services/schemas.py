"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime

# ============= Auth Schemas =============

class UserRegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Validate password requirements:
        - Must contain at least 1 uppercase letter
        - Must contain at least 1 number
        """
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least 1 uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least 1 number')
        return v


class UserLoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Validate password requirements:
        - Must contain at least 1 uppercase letter
        - Must contain at least 1 number
        """
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least 1 uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least 1 number')
        return v


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenRefreshRequest(BaseModel):
    """Token refresh request"""
    refresh_token: str


class UserResponse(BaseModel):
    """User response"""
    user_id: int
    email: str
    full_name: Optional[str]
    is_active: bool
    last_login: Optional[datetime]
    roles: List[str] = []

    class Config:
        from_attributes = True


class LoginResponse(TokenResponse):
    """Login response including authenticated user data."""
    user: UserResponse


# ============= Role & Permission Schemas =============

class PermissionResponse(BaseModel):
    """Permission response"""
    permission_id: int
    name: str
    description: Optional[str]
    resource: str
    action: str

    class Config:
        from_attributes = True


class RoleRequest(BaseModel):
    """Role creation request"""
    name: str
    description: Optional[str] = None


class RoleResponse(BaseModel):
    """Role response"""
    role_id: int
    name: str
    description: Optional[str]
    is_system: bool
    role_permissions: List[PermissionResponse] = []

    class Config:
        from_attributes = True


class RolePermissionRequest(BaseModel):
    """Role permission assignment request"""
    permission_id: int


# ============= Project Schemas =============

class ProjectCreateRequest(BaseModel):
    """Project creation request"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    workspace_id: int
    team_ids: List[int] = []


class ProjectUpdateRequest(BaseModel):
    """Project update request"""
    name: Optional[str] = None
    description: Optional[str] = None
    version: int  # For optimistic locking


class ProjectStatusUpdateRequest(BaseModel):
    """Project status update request"""
    status: str  # planning, active, completed, archived
    version: int


class ProjectResponse(BaseModel):
    """Project response"""
    project_id: int
    name: str
    description: Optional[str]
    status: str
    created_by: int
    start_date: Optional[str]
    end_date: Optional[str]
    repository_url: Optional[str]
    repository_type: Optional[str]
    version: int

    class Config:
        from_attributes = True


# ============= Task Schemas =============

class ProjectTaskCreateRequest(BaseModel):
    """Task creation request"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    story_points: Optional[int] = Field(None, ge=1, le=21)
    assigned_to: Optional[int] = None
    priority: str = "medium"  # high, medium, low
    deadline: Optional[str] = None


class ProjectTaskUpdateRequest(BaseModel):
    """Task update request"""
    title: Optional[str] = None
    description: Optional[str] = None
    story_points: Optional[int] = Field(None, ge=1, le=21)
    priority: Optional[str] = None
    deadline: Optional[str] = None
    version: int  # For optimistic locking


class ProjectTaskStatusUpdateRequest(BaseModel):
    """Task status update request"""
    status: str  # backlog, in_progress, in_review, completed, closed
    version: int


class ProjectTaskWorkloadRequest(BaseModel):
    """Workload logging request"""
    work_date: str  # ISO date
    hours_worked: float = Field(..., gt=0, le=24)
    description: Optional[str] = None


class ProjectTaskCommentRequest(BaseModel):
    """Comment creation request"""
    content: str = Field(..., min_length=1)


class ProjectTaskResponse(BaseModel):
    """Task response"""
    task_id: int
    project_id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    story_points: Optional[int]
    assigned_to: Optional[int]
    deadline: Optional[str]
    version: int

    class Config:
        from_attributes = True


# ============= Team Schemas =============

class TeamCreateRequest(BaseModel):
    """Team creation request"""
    name: str = Field(..., min_length=1, max_length=100)
    category_id: int
    description: Optional[str] = None
    capacity_hours: float = 160


class TeamAddMemberRequest(BaseModel):
    """Add team member request"""
    worker_id: int
    role: str = "member"


class TeamResponse(BaseModel):
    """Team response"""
    team_id: int
    name: str
    category_id: int
    description: Optional[str]
    status: str
    capacity_hours: float

    class Config:
        from_attributes = True


# ============= Worker Schemas =============

class WorkerCreateRequest(BaseModel):
    """Worker creation request"""
    full_name: str
    email: EmailStr
    division_id: int
    phone: Optional[str] = None
    skills: Optional[List[str]] = None


class WorkerResponse(BaseModel):
    """Worker response"""
    worker_id: int
    full_name: str
    email: str
    division_id: int
    employment_status: str

    class Config:
        from_attributes = True


# ============= KPI Schemas =============

class WorkerKPIResponse(BaseModel):
    """Worker KPI response"""
    kpi_id: int
    worker_id: int
    project_id: int
    score: float
    is_manual_override: bool
    override_reason: Optional[str]

    class Config:
        from_attributes = True


class WorkerKPISummaryResponse(BaseModel):
    """Worker KPI summary response"""
    summary_id: int
    worker_id: int
    average_score: Optional[float]
    total_projects: int
    peer_percentile: Optional[int]

    class Config:
        from_attributes = True


# ============= AI Assistant Schemas =============

class AIWorkflowRequest(BaseModel):
    """AI assistant workflow request."""
    prompt: str = Field(..., min_length=1)
    context: Dict[str, Any] = Field(default_factory=dict)
    async_mode: bool = False


class AIWorkflowResponse(BaseModel):
    """AI assistant workflow response."""
    workflow: str
    status: str
    model: str
    content: str
    structured_output: Optional[Dict[str, Any]] = None
    usage: Optional[Dict[str, Any]] = None
    source: str = "openrouter"
    job_id: Optional[str] = None


class AIJobResponse(BaseModel):
    """Queued AI job response."""
    job_id: str
    workflow: str
    status: str
    model: str
    result: Optional[AIWorkflowResponse] = None
    error: Optional[str] = None
