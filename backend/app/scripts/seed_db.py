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
    User
)
from app.services import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
)
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
            
            # Seed default permissions
            await seed_permissions(db)
            
            # Link permissions to roles
            await seed_role_permissions(db)
            
            # Seed divisions
            await seed_divisions(db)
            
            # Seed categories
            await seed_categories(db)
            
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


if __name__ == "__main__":
    print("Starting database seeding...\n")
    asyncio.run(seed_database())
    print("\nDatabase seeding finished!")
