"""
FastAPI application initialization
"""
import json

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.exceptions import RequestValidationError
import logging

from app.config import get_settings
from app.services.responses import (
    error_response,
    success_response,
    is_enveloped_payload,
    extract_error_message,
)

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def _preserve_headers(headers):
    return {
        key: value
        for key, value in headers.items()
        if key.lower() not in {"content-length", "content-type"}
    }


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

    @app.middleware("http")
    async def wrap_api_responses(request: Request, call_next):
        response = await call_next(request)

        if request.url.path.startswith(("/docs", "/redoc", "/openapi.json")):
            return response

        if response.status_code == 204:
            return response

        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            return response

        body = b""
        if hasattr(response, "body_iterator"):
            async for chunk in response.body_iterator:
                body += chunk
        elif getattr(response, "body", None) is not None:
            body = response.body

        passthrough_response = Response(
            content=body,
            status_code=response.status_code,
            headers=_preserve_headers(response.headers),
            media_type=response.media_type,
        )

        try:
            payload = json.loads(body.decode("utf-8")) if body else None
        except (TypeError, ValueError, UnicodeDecodeError):
            return passthrough_response

        if is_enveloped_payload(payload):
            return passthrough_response

        return JSONResponse(
            content=success_response(data=payload, message="success"),
            status_code=response.status_code,
            headers=_preserve_headers(response.headers),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(
                message=extract_error_message(exc.detail),
                data=None if isinstance(exc.detail, str) else exc.detail,
            ),
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # Serialize validation errors, converting non-serializable objects to strings
        errors = []
        for error in exc.errors():
            serializable_error = {
                'type': error.get('type'),
                'loc': error.get('loc'),
                'msg': error.get('msg'),
                'input': error.get('input'),
            }
            # Only include ctx if it exists and convert non-serializable objects
            if 'ctx' in error and error['ctx']:
                ctx = error['ctx']
                serializable_ctx = {}
                for key, value in ctx.items():
                    try:
                        json.dumps(value)
                        serializable_ctx[key] = value
                    except (TypeError, ValueError):
                        serializable_ctx[key] = str(value)
                serializable_error['ctx'] = serializable_ctx
            errors.append(serializable_error)
        
        return JSONResponse(
            status_code=422,
            content=error_response(
                message="Validation failed",
                data=errors,
            ),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled application error", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content=error_response(
                message="Internal server error",
                data=None,
            ),
        )

    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return success_response(
            data={"status": "ok", "version": settings.API_VERSION},
            message="OK",
        )

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
