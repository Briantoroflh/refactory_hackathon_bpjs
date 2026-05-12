"""
FastAPI application initialization
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging

from app.config import get_settings

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title=settings.API_TITLE,
        version=settings.API_VERSION,
        debug=settings.DEBUG,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1"],  # Configure for production
    )

    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "ok", "version": settings.API_VERSION}

    @app.on_event("startup")
    async def startup():
        """Initialize on startup"""
        logger.info("SprintFlow API starting up...")
        
        # Start background job scheduler
        from app.services.scheduler import start_scheduler
        await start_scheduler()

    @app.on_event("shutdown")
    async def shutdown():
        """Cleanup on shutdown"""
        logger.info("SprintFlow API shutting down...")
        
        # Stop background job scheduler
        from app.services.scheduler import stop_scheduler
        await stop_scheduler()

    # Include routers
    from app.routes.auth import router as auth_router
    from app.routes.users import router as users_router
    from app.routes.projects import router as projects_router
    from app.routes.tasks import router as tasks_router, tasks_assigned_router
    from app.routes.roles import router as roles_router
    from app.routes.teams import router as teams_router, divisions_router, categories_router
    from app.routes.workers import router as workers_router, kpi_router
    from app.routes.commits import router as commits_router
    from app.routes.audit import router as audit_router
    
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(projects_router)
    app.include_router(tasks_router)
    app.include_router(tasks_assigned_router)
    app.include_router(roles_router)
    app.include_router(teams_router)
    app.include_router(divisions_router)
    app.include_router(categories_router)
    app.include_router(workers_router)
    app.include_router(kpi_router)
    app.include_router(commits_router)
    app.include_router(audit_router)

    return app


app = create_app()
