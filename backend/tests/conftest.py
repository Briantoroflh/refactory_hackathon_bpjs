"""
Pytest configuration and test fixtures
"""
# Ensure backend package is importable regardless of current working directory
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient, ASGITransport

from app.main import create_app
from app.models import Base
from app.databases import get_db
from app.services import hash_password


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_db():
    """Create test database and return session"""
    # Create async engine for testing
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create async session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    yield async_session
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def test_app(test_db):
    """Create test FastAPI application"""
    app = create_app()
    
    # Override database dependency
    async def override_get_db():
        async with test_db() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    return app


@pytest.fixture
async def client(test_app):
    """Create test HTTP client"""
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as async_client:
        yield async_client


@pytest.fixture
async def test_user(test_db):
    """Create a test user"""
    async with test_db() as db:
        from app.models import User
        
        user = User(
            email="test@example.com",
            password_hash=hash_password("Test@1234"),
            full_name="Test User",
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user


@pytest.fixture
async def test_admin_user(test_db):
    """Create a test admin user"""
    async with test_db() as db:
        from app.models import User, Role, UserRole
        
        # Create admin role
        admin_role = Role(
            name="admin",
            is_system=True,
        )
        db.add(admin_role)
        await db.flush()
        
        # Create admin user
        user = User(
            email="admin@example.com",
            password_hash=hash_password("Admin@1234"),
            full_name="Admin User",
            is_active=True,
        )
        db.add(user)
        await db.flush()
        
        # Assign admin role
        user_role = UserRole(
            user_id=user.user_id,
            role_id=admin_role.role_id,
        )
        db.add(user_role)
        
        await db.commit()
        await db.refresh(user)
        return user


@pytest.fixture
async def test_project(test_db, test_user):
    """Create a test workspace and project"""
    async with test_db() as db:
        from app.models import Project, ProjectWorkspace
        
        # Create workspace first
        workspace = ProjectWorkspace(
            name="Test Workspace",
            description="Test workspace for projects",
            is_active=True,
        )
        db.add(workspace)
        await db.flush()
        
        # Create project with workspace_id
        project = Project(
            workspace_id=workspace.workspace_id,
            name="Test Project",
            description="Test project description",
            created_by=test_user.user_id,
            status="planning",
        )
        db.add(project)
        await db.commit()
        await db.refresh(project)
        return project


@pytest.fixture
async def test_task(test_db, test_project, test_user):
    """Create a test task"""
    async with test_db() as db:
        from app.models import ProjectTask
        
        task = ProjectTask(
            project_id=test_project.project_id,
            title="Test Task",
            description="Test task description",
            story_points=5,
            assigned_to=test_user.user_id,
            priority="medium",
            status="backlog",
            created_by=test_user.user_id,
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task


# Configure pytest
pytest_plugins = []


def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )
