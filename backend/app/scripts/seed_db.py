"""
Database seeding script for initial data setup
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select

from app.config import get_settings
from app.models import (
    Base,
    Role,
    Permission,
    RolePermission,
    Division,
    Category,
    User,
    UserRole,
    Worker,
    WorkerProfile,
    Team,
    TeamMember,
    TeamWorkspace,
    ProjectWorkspace,
    Project,
    ProjectTeam,
    ProjectTeamSelection,
    ProjectTeamMember,
    ProjectDetail,
    ProjectDetailImage,
    ProjectDetailDoc,
    ProjectTask,
    ProjectTaskWorkload,
    ProjectTaskHistory,
    ProjectTaskComment,
    ProjectTaskSummary,
    ProjectSummary,
    WorkerKPI,
    WorkerKPISummary,
    ProjectCommitTracking,
    CommitChangeLogs,
    UserLog,
    AuditSystemLog,
    GlobalJob,
    GitLabRepository,
    Commit,
)
from app.services import hash_password
from datetime import datetime, timezone


async def seed_database():
    """Seed database with initial data"""
    settings = get_settings()
    
    # Create async engine and session
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as db:
        try:
            # Seed default users
            await seed_users(db)

            # Seed default roles
            await seed_roles(db)

            # Seed user-role assignments
            await seed_user_roles(db)
            
            # Seed default permissions
            await seed_permissions(db)
            
            # Link permissions to roles
            await seed_role_permissions(db)
            
            # Seed divisions
            await seed_divisions(db)
            
            # Seed categories
            await seed_categories(db)

            # Seed workers
            await seed_workers(db)

            # Seed teams
            await seed_teams(db)

            # Seed team members
            await seed_team_members(db)

            # Seed worker profiles
            await seed_worker_profiles(db)

            # Seed project workspaces and projects
            await seed_project_data(db)

            # Seed project/task-related records
            await seed_project_activity(db)

            # Seed KPI records
            await seed_kpis(db)

            # Seed audit, job, and GitLab records
            await seed_audit_and_integrations(db)
            
            print("✓ Database seeding completed successfully")
            
        except Exception as e:
            print(f"✗ Database seeding failed: {str(e)}")
            await db.rollback()
            raise

async def seed_users(db: AsyncSession):
    """ Seed default users """
    users_data = [
        {
            "email": "admin@example.com", 
            "password": hash_password("12345"), 
            "full_name": "Basir", 
            "is_active": True
        }
    ]

    for data in users_data:
        # 1. Cek apakah user sudah ada berdasarkan email
        stmt = select(User).where(User.email == data["email"])
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            print(f"  User '{data['email']}' already exists, skipping")
            continue

        # 2. Buat instance user
        user_obj = User(
            email=data['email'],
            password_hash=data['password'],
            full_name=data["full_name"],
            is_active=data['is_active'],
            # Gunakan naive datetime jika database Anda TIMESTAMP WITHOUT TIME ZONE
            last_login=datetime.now() 
        )
        
        db.add(user_obj)
        print(f"  ✓ Created user: {data['email']}")

    await db.commit()


async def seed_roles(db: AsyncSession):
    """Seed default roles"""
    roles = [
        {
            "name": "admin",
            "description": "Administrator with full system access",
            "is_system": True
        },
        {
            "name": "project_manager",
            "description": "Project Manager - can manage projects and teams",
            "is_system": True
        },
        {
            "name": "team_lead",
            "description": "Team Lead - can manage team members and tasks",
            "is_system": True
        },
        {
            "name": "engineer",
            "description": "Engineer/Developer - can view and update assigned tasks",
            "is_system": True
        },
    ]
    
    for role_data in roles:
        # Check if role already exists
        stmt = select(Role).where(Role.name == role_data["name"])
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            print(f"  Role '{role_data['name']}' already exists, skipping")
            continue
        
        role = Role(
            name=role_data["name"],
            description=role_data.get("description"),
            is_system=role_data.get("is_system", False)
        )
        db.add(role)
        print(f"  ✓ Created role: {role_data['name']}")
    
    await db.commit()


async def seed_permissions(db: AsyncSession):
    """Seed default permissions"""
    permissions = [
        {"name": "read_projects", "description": "Read project information"},
        {"name": "create_projects", "description": "Create new projects"},
        {"name": "update_projects", "description": "Update project information"},
        {"name": "delete_projects", "description": "Delete projects"},
        {"name": "read_tasks", "description": "Read task information"},
        {"name": "create_tasks", "description": "Create new tasks"},
        {"name": "update_tasks", "description": "Update task information"},
        {"name": "delete_tasks", "description": "Delete tasks"},
        {"name": "read_users", "description": "Read user information"},
        {"name": "manage_users", "description": "Manage user accounts and permissions"},
        {"name": "read_audit_logs", "description": "Read audit logs"},
        {"name": "manage_roles", "description": "Manage roles and permissions"},
        {"name": "manage_teams", "description": "Manage team membership"},
        {"name": "view_kpi", "description": "View KPI scores"},
        {"name": "update_kpi", "description": "Manually update KPI scores"},
    ]
    
    for perm_data in permissions:
        # Check if permission already exists
        stmt = select(Permission).where(Permission.name == perm_data["name"])
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            print(f"  Permission '{perm_data['name']}' already exists, skipping")
            continue
        # Derive action and resource from permission name when not provided
        def _parse_permission_name(name: str):
            # Expected formats: action_resource (e.g., read_projects)
            # Fallbacks: manage_users, view_kpi, etc.
            parts = name.split("_", 1)
            if len(parts) == 2:
                action, resource = parts
            else:
                # If no underscore, treat whole as resource with 'manage' action
                action = "manage"
                resource = parts[0]
            # normalize resource to singular form when simple plural exists
            if resource.endswith("s") and len(resource) > 1:
                resource = resource[:-1]
            return action, resource

        action, resource = _parse_permission_name(perm_data["name"])

        permission = Permission(
            name=perm_data["name"],
            description=perm_data.get("description"),
            resource=resource or "global",
            action=action or "manage",
        )
        db.add(permission)
        print(f"  ✓ Created permission: {perm_data['name']}")
    
    await db.commit()


async def seed_role_permissions(db: AsyncSession):
    """Assign permissions to roles"""
    role_permission_map = {
        "admin": [
            "read_projects", "create_projects", "update_projects", "delete_projects",
            "read_tasks", "create_tasks", "update_tasks", "delete_tasks",
            "read_users", "manage_users", "read_audit_logs", "manage_roles",
            "manage_teams", "view_kpi", "update_kpi"
        ],
        "project_manager": [
            "read_projects", "create_projects", "update_projects",
            "read_tasks", "create_tasks", "update_tasks",
            "read_users", "manage_teams", "view_kpi", "update_kpi"
        ],
        "team_lead": [
            "read_projects", "read_tasks", "create_tasks", "update_tasks",
            "read_users", "manage_teams", "view_kpi"
        ],
        "engineer": [
            "read_projects", "read_tasks", "update_tasks", "read_users", "view_kpi"
        ],
    }
    
    for role_name, perm_names in role_permission_map.items():
        # Get role
        stmt = select(Role).where(Role.name == role_name)
        result = await db.execute(stmt)
        role = result.scalar_one_or_none()
        
        if not role:
            print(f"  ✗ Role '{role_name}' not found")
            continue
        
        for perm_name in perm_names:
            # Get permission
            stmt = select(Permission).where(Permission.name == perm_name)
            result = await db.execute(stmt)
            permission = result.scalar_one_or_none()
            
            if not permission:
                print(f"  ✗ Permission '{perm_name}' not found")
                continue
            
            # Check if relationship already exists
            stmt = select(RolePermission).where(
                (RolePermission.role_id == role.role_id) &
                (RolePermission.permission_id == permission.permission_id)
            )
            result = await db.execute(stmt)
            if result.scalar_one_or_none():
                continue
            
            # Create relationship
            role_permission = RolePermission(
                role_id=role.role_id,
                permission_id=permission.permission_id
            )
            db.add(role_permission)
        
        print(f"  ✓ Assigned {len(perm_names)} permissions to role: {role_name}")
    
    await db.commit()


async def seed_divisions(db: AsyncSession):
    """Seed default divisions"""
    divisions = [
        {"name": "Engineering", "description": "Engineering division"},
        {"name": "Product", "description": "Product division"},
        {"name": "Operations", "description": "Operations division"},
    ]
    
    for div_data in divisions:
        # Check if division already exists
        stmt = select(Division).where(Division.name == div_data["name"])
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            print(f"  Division '{div_data['name']}' already exists, skipping")
            continue
        
        division = Division(
            name=div_data["name"],
            description=div_data.get("description"),
        )
        db.add(division)
        print(f"  ✓ Created division: {div_data['name']}")
    
    await db.commit()


async def seed_categories(db: AsyncSession):
    """Seed default categories"""
    categories = [
        {"name": "Frontend", "description": "Frontend development", "division": "Engineering"},
        {"name": "Backend", "description": "Backend development", "division": "Engineering"},
        {"name": "DevOps", "description": "DevOps and infrastructure", "division": "Operations"},
        {"name": "QA", "description": "Quality assurance", "division": "Operations"},
        {"name": "Design", "description": "Design and UX", "division": "Product"},
    ]
    
    for cat_data in categories:
        # Check if category already exists
        stmt = select(Category).where(Category.name == cat_data["name"])
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            print(f"  Category '{cat_data['name']}' already exists, skipping")
            continue
        
        # Determine division_id: lookup division by name if provided, else default to 'Engineering'
        division_name = cat_data.get("division") or "Engineering"
        stmt = select(Division).where(Division.name == division_name)
        res = await db.execute(stmt)
        division = res.scalar_one_or_none()
        if not division:
            # Fallback: use any existing division
            stmt = select(Division).limit(1)
            res = await db.execute(stmt)
            division = res.scalar_one_or_none()

        division_id = division.division_id if division else None

        category = Category(
            name=cat_data["name"],
            division_id=division_id,
            description=cat_data.get("description"),
        )
        db.add(category)
        print(f"  ✓ Created category: {cat_data['name']}")
    
    await db.commit()


async def seed_workers(db: AsyncSession):
    """Seed default workers"""
    workers = [
        {
            "full_name": "Basir",
            "email": "basir.worker@example.com",
            "division": "Engineering",
            "phone": None,
            "skills": ["python", "fastapi", "sqlalchemy"],
        },
        {
            "full_name": "Dina Product",
            "email": "dina.product@example.com",
            "division": "Product",
            "phone": None,
            "skills": ["product management", "roadmap"],
        },
        {
            "full_name": "Raka Frontend",
            "email": "raka.frontend@example.com",
            "division": "Engineering",
            "phone": None,
            "skills": ["nextjs", "typescript"],
        },
        {
            "full_name": "Sinta Backend",
            "email": "sinta.backend@example.com",
            "division": "Engineering",
            "phone": None,
            "skills": ["python", "postgresql"],
        },
        {
            "full_name": "Bagas QA",
            "email": "bagas.qa@example.com",
            "division": "Operations",
            "phone": None,
            "skills": ["testing", "automation"],
        },
    ]

    for worker_data in workers:
        stmt = select(Worker).where(Worker.email == worker_data["email"])
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            print(f"  Worker '{worker_data['email']}' already exists, skipping")
            continue

        division_name = worker_data.get("division") or "Engineering"
        stmt = select(Division).where(Division.name == division_name)
        div_result = await db.execute(stmt)
        division = div_result.scalar_one_or_none()

        if not division:
            stmt = select(Division).limit(1)
            div_result = await db.execute(stmt)
            division = div_result.scalar_one_or_none()

        if not division:
            print(f"  ✗ No division found for worker '{worker_data['email']}', skipping")
            continue

        worker = Worker(
            full_name=worker_data["full_name"],
            email=worker_data["email"],
            division_id=division.division_id,
            phone=worker_data.get("phone"),
            skills=worker_data.get("skills", []),
            employment_status="active",
        )
        db.add(worker)
        print(f"  ✓ Created worker: {worker_data['email']}")

    await db.commit()


async def seed_teams(db: AsyncSession):
    """Seed default teams"""
    teams = [
        {
            "name": "Backend Team",
            "category": "Backend",
            "description": "Core backend team",
            "capacity_hours": 320,
            "status": "active",
        },
        {
            "name": "Frontend Team",
            "category": "Frontend",
            "description": "Frontend web team",
            "capacity_hours": 320,
            "status": "active",
        },
        {
            "name": "QA Team",
            "category": "QA",
            "description": "Quality assurance team",
            "capacity_hours": 160,
            "status": "active",
        },
    ]

    for team_data in teams:
        stmt = select(Team).where(Team.name == team_data["name"])
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            print(f"  Team '{team_data['name']}' already exists, skipping")
            continue

        stmt = select(Category).where(Category.name == team_data["category"])
        cat_result = await db.execute(stmt)
        category = cat_result.scalar_one_or_none()

        if not category:
            print(f"  ✗ Category '{team_data['category']}' not found, skipping team")
            continue

        team = Team(
            name=team_data["name"],
            category_id=category.category_id,
            description=team_data.get("description"),
            capacity_hours=team_data.get("capacity_hours", 160),
            status=team_data.get("status", "active"),
        )
        db.add(team)
        print(f"  ✓ Created team: {team_data['name']}")

    await db.commit()


async def seed_team_members(db: AsyncSession):
    """Seed default team members"""
    members = {
        "Backend Team": [
            {"worker_email": "sinta.backend@example.com", "role": "lead"},
            {"worker_email": "basir.worker@example.com", "role": "member"},
        ],
        "Frontend Team": [
            {"worker_email": "raka.frontend@example.com", "role": "lead"},
        ],
        "QA Team": [
            {"worker_email": "bagas.qa@example.com", "role": "lead"},
            {"worker_email": "dina.product@example.com", "role": "member"},
        ],
    }

    for team_name, team_members in members.items():
        stmt = select(Team).where(Team.name == team_name)
        team_result = await db.execute(stmt)
        team = team_result.scalar_one_or_none()

        if not team:
            print(f"  ✗ Team '{team_name}' not found, skipping members")
            continue

        for member_data in team_members:
            stmt = select(Worker).where(Worker.email == member_data["worker_email"])
            worker_result = await db.execute(stmt)
            worker = worker_result.scalar_one_or_none()

            if not worker:
                print(f"  ✗ Worker '{member_data['worker_email']}' not found, skipping")
                continue

            stmt = select(TeamMember).where(
                (TeamMember.team_id == team.team_id) & (TeamMember.worker_id == worker.worker_id)
            )
            existing_result = await db.execute(stmt)
            if existing_result.scalar_one_or_none():
                continue

            team_member = TeamMember(
                team_id=team.team_id,
                worker_id=worker.worker_id,
                role=member_data.get("role", "member"),
                is_active=True,
                join_date=datetime.now(timezone.utc).isoformat(),
            )
            db.add(team_member)

        print(f"  ✓ Assigned members to team: {team_name}")

    await db.commit()


async def seed_user_roles(db: AsyncSession):
    """Assign roles to seeded users"""
    # Map user email -> list of role names
    assignments = {
        "admin@example.com": ["admin"],
    }

    for email, role_names in assignments.items():
        # find user
        stmt = select(User).where(User.email == email)
        res = await db.execute(stmt)
        user = res.scalar_one_or_none()

        if not user:
            print(f"  ✗ User '{email}' not found, skipping role assignments")
            continue

        for role_name in role_names:
            stmt = select(Role).where(Role.name == role_name)
            res = await db.execute(stmt)
            role = res.scalar_one_or_none()

            if not role:
                print(f"  ✗ Role '{role_name}' not found, skipping")
                continue

            # check if user-role already exists
            stmt = select(UserRole).where(
                (UserRole.user_id == user.user_id) & (UserRole.role_id == role.role_id)
            )
            res = await db.execute(stmt)
            if res.scalar_one_or_none():
                continue

            db.add(UserRole(user_id=user.user_id, role_id=role.role_id))

        print(f"  ✓ Assigned roles to user: {email}")

    await db.commit()


async def _get_one(db: AsyncSession, model, *conditions):
    stmt = select(model)
    for condition in conditions:
        stmt = stmt.where(condition)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def seed_worker_profiles(db: AsyncSession):
    """Seed extended worker profile records"""
    profiles = [
        {
            "worker_email": "basir.worker@example.com",
            "avatar_url": "https://example.com/avatars/basir.png",
            "bio": "Backend engineer focused on API design and data workflows.",
            "linkedin_url": "https://linkedin.com/in/basir",
            "github_url": "https://github.com/basir",
            "preferred_contact": "email",
            "timezone": "Asia/Jakarta",
            "languages": ["id", "en"],
            "certifications": ["AWS Cloud Practitioner"],
        },
        {
            "worker_email": "raka.frontend@example.com",
            "avatar_url": "https://example.com/avatars/raka.png",
            "bio": "Frontend engineer building responsive product experiences.",
            "linkedin_url": "https://linkedin.com/in/raka",
            "github_url": "https://github.com/raka",
            "preferred_contact": "email",
            "timezone": "Asia/Jakarta",
            "languages": ["id", "en"],
            "certifications": ["Next.js Certified Developer"],
        },
        {
            "worker_email": "sinta.backend@example.com",
            "avatar_url": "https://example.com/avatars/sinta.png",
            "bio": "Backend engineer supporting services and database layers.",
            "linkedin_url": "https://linkedin.com/in/sinta",
            "github_url": "https://github.com/sinta",
            "preferred_contact": "email",
            "timezone": "Asia/Jakarta",
            "languages": ["id", "en"],
            "certifications": ["PostgreSQL Associate"],
        },
    ]

    for profile_data in profiles:
        worker = await _get_one(db, Worker, Worker.email == profile_data["worker_email"])
        if not worker:
            print(f"  ✗ Worker '{profile_data['worker_email']}' not found, skipping profile")
            continue

        existing_profile = await _get_one(db, WorkerProfile, WorkerProfile.worker_id == worker.worker_id)
        if existing_profile:
            print(f"  Worker profile for '{profile_data['worker_email']}' already exists, skipping")
            continue

        profile = WorkerProfile(
            worker_id=worker.worker_id,
            avatar_url=profile_data.get("avatar_url"),
            bio=profile_data.get("bio"),
            linkedin_url=profile_data.get("linkedin_url"),
            github_url=profile_data.get("github_url"),
            preferred_contact=profile_data.get("preferred_contact"),
            timezone=profile_data.get("timezone"),
            languages=profile_data.get("languages"),
            certifications=profile_data.get("certifications"),
        )
        db.add(profile)
        print(f"  ✓ Created worker profile: {profile_data['worker_email']}")

    await db.commit()


async def seed_project_data(db: AsyncSession):
    """Seed project workspaces, project teams, and related project metadata"""
    admin = await _get_one(db, User, User.email == "admin@example.com")
    backend_team = await _get_one(db, Team, Team.name == "Backend Team")
    frontend_team = await _get_one(db, Team, Team.name == "Frontend Team")
    backend_worker = await _get_one(db, Worker, Worker.email == "basir.worker@example.com")
    frontend_worker = await _get_one(db, Worker, Worker.email == "raka.frontend@example.com")
    sinta_worker = await _get_one(db, Worker, Worker.email == "sinta.backend@example.com")

    if not admin or not backend_team or not frontend_team:
        print("  ✗ Missing core seed data for project setup, skipping project graph")
        return

    workspace = await _get_one(db, ProjectWorkspace, ProjectWorkspace.name == "Platform Workspace")
    if not workspace:
        workspace = ProjectWorkspace(
            name="Platform Workspace",
            description="Workspace for internal platform delivery",
            is_active=True,
        )
        db.add(workspace)
        await db.flush()
        print("  ✓ Created project workspace: Platform Workspace")

    project = await _get_one(db, Project, Project.name == "Internal Platform")
    if not project:
        project = Project(
            workspace_id=workspace.workspace_id,
            name="Internal Platform",
            description="Core internal platform used for project coordination",
            status="active",
            created_by=admin.user_id,
            start_date=datetime.now(timezone.utc).date().isoformat(),
            repository_url="https://gitlab.example.com/platform/internal-platform",
            repository_token="seed-token",
            repository_type="gitlab",
            version=1,
        )
        db.add(project)
        await db.flush()
        print("  ✓ Created project: Internal Platform")

    team_workspace_targets = [backend_team, frontend_team]
    for team in team_workspace_targets:
        existing_team_workspace = await _get_one(
            db,
            TeamWorkspace,
            TeamWorkspace.team_id == team.team_id,
            TeamWorkspace.workspace_id == workspace.workspace_id,
        )
        if existing_team_workspace:
            continue
        db.add(
            TeamWorkspace(
                team_id=team.team_id,
                workspace_id=workspace.workspace_id,
                is_primary=(team.team_id == backend_team.team_id),
            )
        )
        print(f"  ✓ Linked team to workspace: {team.name}")

    project_team_targets = [backend_team, frontend_team]
    for team in project_team_targets:
        existing_project_team = await _get_one(
            db,
            ProjectTeam,
            ProjectTeam.project_id == project.project_id,
            ProjectTeam.team_id == team.team_id,
        )
        if existing_project_team:
            project_team = existing_project_team
        else:
            project_team = ProjectTeam(
                project_id=project.project_id,
                team_id=team.team_id,
                role="lead" if team.team_id == backend_team.team_id else "contributor",
            )
            db.add(project_team)
            await db.flush()

        existing_selection = await _get_one(db, ProjectTeamSelection, ProjectTeamSelection.project_team_id == project_team.project_team_id)
        if not existing_selection:
            db.add(
                ProjectTeamSelection(
                    project_team_id=project_team.project_team_id,
                    status="approved",
                    selection_notes="Seeded team assignment for the internal platform project.",
                )
            )

        assigned_workers = []
        if team.team_id == backend_team.team_id and sinta_worker:
            assigned_workers = [(sinta_worker, "lead")]
        elif team.team_id == frontend_team.team_id and frontend_worker:
            assigned_workers = [(frontend_worker, "engineer")]
        elif backend_worker:
            assigned_workers = [(backend_worker, "engineer")]

        for worker, role in assigned_workers:
            existing_project_member = await _get_one(
                db,
                ProjectTeamMember,
                ProjectTeamMember.project_team_id == project_team.project_team_id,
                ProjectTeamMember.worker_id == worker.worker_id,
            )
            if existing_project_member:
                continue
            db.add(
                ProjectTeamMember(
                    project_team_id=project_team.project_team_id,
                    worker_id=worker.worker_id,
                    role=role,
                    allocation_percentage=100,
                )
            )

    detail = await _get_one(db, ProjectDetail, ProjectDetail.project_id == project.project_id)
    if not detail:
        detail = ProjectDetail(
            project_id=project.project_id,
            content="Initial seeded project detail record for the internal platform.",
        )
        db.add(detail)
        await db.flush()
        print("  ✓ Created project detail")

    if not await _get_one(db, ProjectDetailImage, ProjectDetailImage.detail_id == detail.detail_id):
        db.add(
            ProjectDetailImage(
                detail_id=detail.detail_id,
                image_url="https://example.com/projects/internal-platform/overview.png",
                caption="Seeded overview image",
            )
        )

    if not await _get_one(db, ProjectDetailDoc, ProjectDetailDoc.detail_id == detail.detail_id):
        db.add(
            ProjectDetailDoc(
                detail_id=detail.detail_id,
                doc_url="https://example.com/projects/internal-platform/spec.pdf",
                doc_name="Internal Platform Spec",
                doc_type="pdf",
            )
        )

    existing_repo = await _get_one(db, GitLabRepository, GitLabRepository.project_id == project.project_id)
    if not existing_repo:
        db.add(
            GitLabRepository(
                project_id=project.project_id,
                gitlab_project_id=9001,
                gitlab_url="https://gitlab.example.com/platform/internal-platform",
                gitlab_access_token="seed-gitlab-token",
                last_sync_timestamp=datetime.now(),
            )
        )
        print("  ✓ Created GitLab repository link")

    await db.commit()


async def seed_project_activity(db: AsyncSession):
    """Seed tasks, task histories, task comments, workloads, and summaries"""
    admin = await _get_one(db, User, User.email == "admin@example.com")
    basir_worker = await _get_one(db, Worker, Worker.email == "basir.worker@example.com")
    raka_worker = await _get_one(db, Worker, Worker.email == "raka.frontend@example.com")
    project = await _get_one(db, Project, Project.name == "Internal Platform")

    if not admin or not project:
        print("  ✗ Missing project seed data, skipping task activity")
        return

    task_specs = [
        {
            "title": "Design API contract",
            "description": "Define backend contract for the internal platform dashboard.",
            "status": "completed",
            "priority": "high",
            "story_points": 5,
            "assigned_to": basir_worker.worker_id if basir_worker else None,
            "deadline": datetime.now(timezone.utc).date().isoformat(),
        },
        {
            "title": "Implement dashboard shell",
            "description": "Build the initial frontend shell and routing structure.",
            "status": "in_progress",
            "priority": "medium",
            "story_points": 8,
            "assigned_to": raka_worker.worker_id if raka_worker else None,
            "deadline": datetime.now(timezone.utc).date().isoformat(),
        },
    ]

    seeded_tasks = []
    for task_spec in task_specs:
        task = await _get_one(db, ProjectTask, ProjectTask.title == task_spec["title"])
        if not task:
            task = ProjectTask(
                project_id=project.project_id,
                title=task_spec["title"],
                description=task_spec.get("description"),
                status=task_spec.get("status", "backlog"),
                priority=task_spec.get("priority", "medium"),
                story_points=task_spec.get("story_points"),
                assigned_to=task_spec.get("assigned_to"),
                created_by=admin.user_id,
                deadline=task_spec.get("deadline"),
                version=1,
            )
            db.add(task)
            await db.flush()
            print(f"  ✓ Created task: {task_spec['title']}")
        seeded_tasks.append(task)

    completed_task = next((task for task in seeded_tasks if task.status == "completed"), None)
    active_task = next((task for task in seeded_tasks if task.status != "completed"), None)

    if completed_task:
        if not await _get_one(db, ProjectTaskWorkload, ProjectTaskWorkload.task_id == completed_task.task_id):
            db.add(
                ProjectTaskWorkload(
                    task_id=completed_task.task_id,
                    worker_id=basir_worker.worker_id if basir_worker else completed_task.assigned_to,
                    work_date=datetime.now(timezone.utc).date().isoformat(),
                    hours_worked=6.5,
                    description="Completed initial backend API contract work.",
                )
            )

        if not await _get_one(db, ProjectTaskHistory, ProjectTaskHistory.task_id == completed_task.task_id):
            db.add(
                ProjectTaskHistory(
                    task_id=completed_task.task_id,
                    action="status_changed",
                    field_name="status",
                    old_value="in_progress",
                    new_value="completed",
                    changed_by=admin.user_id,
                    reason="Seeded completion state",
                )
            )

        if not await _get_one(db, ProjectTaskComment, ProjectTaskComment.task_id == completed_task.task_id):
            db.add(
                ProjectTaskComment(
                    task_id=completed_task.task_id,
                    author_id=admin.user_id,
                    content="Seeded completion comment for the API contract task.",
                    mentions=[admin.user_id],
                    is_resolved=True,
                )
            )

        if not await _get_one(db, ProjectTaskSummary, ProjectTaskSummary.task_id == completed_task.task_id):
            db.add(
                ProjectTaskSummary(
                    task_id=completed_task.task_id,
                    total_effort=6.5,
                    completion_date=datetime.now(timezone.utc).date().isoformat(),
                    contributors=[basir_worker.worker_id] if basir_worker else [],
                    notes="Seeded task summary",
                )
            )

    if active_task:
        if not await _get_one(db, ProjectTaskWorkload, ProjectTaskWorkload.task_id == active_task.task_id):
            db.add(
                ProjectTaskWorkload(
                    task_id=active_task.task_id,
                    worker_id=raka_worker.worker_id if raka_worker else active_task.assigned_to,
                    work_date=datetime.now(timezone.utc).date().isoformat(),
                    hours_worked=3.0,
                    description="Initial frontend implementation work.",
                )
            )

        if not await _get_one(db, ProjectTaskHistory, ProjectTaskHistory.task_id == active_task.task_id):
            db.add(
                ProjectTaskHistory(
                    task_id=active_task.task_id,
                    action="assigned",
                    field_name="assigned_to",
                    old_value=None,
                    new_value=str(active_task.assigned_to),
                    changed_by=admin.user_id,
                    reason="Seeded assignment event",
                )
            )

        if not await _get_one(db, ProjectTaskComment, ProjectTaskComment.task_id == active_task.task_id):
            db.add(
                ProjectTaskComment(
                    task_id=active_task.task_id,
                    author_id=admin.user_id,
                    content="Seeded work-in-progress comment for the dashboard shell task.",
                    mentions=[admin.user_id],
                    is_resolved=False,
                )
            )

    if not await _get_one(db, ProjectSummary, ProjectSummary.project_id == project.project_id):
        db.add(
            ProjectSummary(
                project_id=project.project_id,
                total_tasks=len(seeded_tasks),
                completed_tasks=1 if completed_task else 0,
                total_effort=9.5,
                actual_duration_days=14,
                key_achievements="Seeded end-to-end project summary",
            )
        )

    await db.commit()


async def seed_kpis(db: AsyncSession):
    """Seed KPI measurements and summaries"""
    project = await _get_one(db, Project, Project.name == "Internal Platform")
    basir_worker = await _get_one(db, Worker, Worker.email == "basir.worker@example.com")
    raka_worker = await _get_one(db, Worker, Worker.email == "raka.frontend@example.com")

    if not project or not basir_worker:
        print("  ✗ Missing project or worker seed data, skipping KPI records")
        return

    kpi_rows = [
        {
            "worker_id": basir_worker.worker_id,
            "score": 91.25,
            "is_manual_override": False,
            "calculated_by": "system",
            "metrics": {"completed_tasks": 1, "review_cycles": 1, "bugs": 0},
        },
        {
            "worker_id": raka_worker.worker_id if raka_worker else basir_worker.worker_id,
            "score": 88.5,
            "is_manual_override": True,
            "override_reason": "Seeded manual calibration",
            "calculated_by": "admin@example.com",
            "metrics": {"completed_tasks": 0, "review_cycles": 1, "bugs": 0},
        },
    ]

    for row in kpi_rows:
        existing_kpi = await _get_one(db, WorkerKPI, WorkerKPI.worker_id == row["worker_id"], WorkerKPI.project_id == project.project_id)
        if existing_kpi:
            continue
        db.add(
            WorkerKPI(
                worker_id=row["worker_id"],
                project_id=project.project_id,
                score=row["score"],
                is_manual_override=row.get("is_manual_override", False),
                override_reason=row.get("override_reason"),
                metrics=row.get("metrics"),
                calculated_by=row.get("calculated_by"),
            )
        )

    summary_rows = [
        {
            "worker_id": basir_worker.worker_id,
            "average_score": 91.25,
            "total_projects": 1,
            "peer_percentile": 95,
            "trend_data": {"weeks": [88, 90, 91]},
        },
        {
            "worker_id": raka_worker.worker_id if raka_worker else basir_worker.worker_id,
            "average_score": 88.5,
            "total_projects": 1,
            "peer_percentile": 87,
            "trend_data": {"weeks": [84, 86, 89]},
        },
    ]

    for row in summary_rows:
        existing_summary = await _get_one(db, WorkerKPISummary, WorkerKPISummary.worker_id == row["worker_id"])
        if existing_summary:
            continue
        db.add(
            WorkerKPISummary(
                worker_id=row["worker_id"],
                average_score=row.get("average_score"),
                total_projects=row.get("total_projects", 0),
                peer_percentile=row.get("peer_percentile"),
                trend_data=row.get("trend_data"),
                last_updated=datetime.now(timezone.utc).isoformat(),
            )
        )

    await db.commit()


async def seed_audit_and_integrations(db: AsyncSession):
    """Seed audit logs, scheduled jobs, commit tracking, and GitLab commits"""
    admin = await _get_one(db, User, User.email == "admin@example.com")
    project = await _get_one(db, Project, Project.name == "Internal Platform")
    basir_worker = await _get_one(db, Worker, Worker.email == "basir.worker@example.com")
    repo = await _get_one(db, GitLabRepository, GitLabRepository.project_id == project.project_id) if project else None

    if not admin:
        print("  ✗ Missing admin user, skipping audit records")
        return

    if project and basir_worker:
        if not await _get_one(db, ProjectCommitTracking, ProjectCommitTracking.commit_hash == "seed-commit-0001"):
            db.add(
                ProjectCommitTracking(
                    project_id=project.project_id,
                    commit_hash="seed-commit-0001",
                    author_email=basir_worker.email,
                    worker_id=basir_worker.worker_id,
                    commit_message="Seeded initial backend integration commit",
                    commit_date=datetime.now(timezone.utc).isoformat(),
                    files_changed=3,
                    insertions=120,
                    deletions=0,
                    file_list=["app/main.py", "app/routes/projects.py", "app/services/projects.py"],
                )
            )

    if project and not await _get_one(db, CommitChangeLogs, CommitChangeLogs.project_id == project.project_id):
        db.add(
            CommitChangeLogs(
                project_id=project.project_id,
                action="commit_sync",
                commits_fetched=1,
                commits_failed=0,
                sync_duration_seconds=2,
                error_message=None,
                sync_date=datetime.now(timezone.utc).isoformat(),
            )
        )

    if not await _get_one(db, UserLog, UserLog.user_id == admin.user_id, UserLog.action == "login"):
        db.add(
            UserLog(
                user_id=admin.user_id,
                action="login",
                resource="auth",
                ip_address="127.0.0.1",
                user_agent="Seeder",
                status="success",
                details={"seeded": True},
                resource_type="auth",
            )
        )

    if project and not await _get_one(db, AuditSystemLog, AuditSystemLog.changed_by == admin.user_id, AuditSystemLog.action == "project_seeded"):
        db.add(
            AuditSystemLog(
                action="project_seeded",
                resource_type="project",
                resource_id=project.project_id,
                changed_by=admin.user_id,
                field_name="status",
                old_value="planning",
                new_value="active",
                reason="Seeded initial project state",
                details={"seeded": True},
                severity="info",
            )
        )

    if not await _get_one(db, GlobalJob, GlobalJob.job_name == "commit_sync_job"):
        db.add(
            GlobalJob(
                job_name="commit_sync_job",
                job_type="commit_sync",
                status="completed",
                last_run=datetime.now(timezone.utc).isoformat(),
                next_run=datetime.now(timezone.utc).isoformat(),
                error_message=None,
                retry_count=0,
                max_retries=3,
                details={"seeded": True},
            )
        )

    if repo and not await _get_one(db, Commit, Commit.repository_id == repo.id, Commit.git_hash == "seedgit0001"):
        db.add(
            Commit(
                repository_id=repo.id,
                git_hash="seedgit0001",
                author_name="Basir",
                author_email=basir_worker.email if basir_worker else "basir.worker@example.com",
                message="Seeded GitLab commit for analytics coverage",
                committed_at=datetime.now(),
                branch="main",
            )
        )

    await db.commit()


if __name__ == "__main__":
    print("Starting database seeding...\n")
    asyncio.run(seed_database())
    print("\nDatabase seeding finished!")
