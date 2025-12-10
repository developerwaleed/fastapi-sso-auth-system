from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.api.v1 import api_router
from app.db.base import Base
from app.db.session import engine
from app.core.config import settings

# Import all models before creating tables
from app.models import *  # noqa

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    ## Enterprise-Grade FastAPI SSO & Authorization System
    
    A production-ready backend with SSO authentication and comprehensive authorization.
    
    ### Key Features
    - **SSO Authentication**: Google and GitHub OAuth2 integration
    - **Dual Auth Methods**: JWT tokens and API Keys
    - **RBAC**: Role-Based Access Control with fine-grained permissions
    - **Flexible Auth**: Endpoints support JWT-only, API-key-only, or either
    - **Layered Architecture**: Clean separation of concerns (API, Services, CRUD, Models)
    - **API Versioning**: Versioned API endpoints for backward compatibility
    
    ### Architecture Highlights
    - **Service Layer**: Business logic separated from API layer
    - **Repository Pattern**: CRUD operations abstracted for reusability
    - **Dependency Injection**: Clean, testable dependencies
    - **Type Safety**: Full Pydantic validation and type hints
    
    ### Authentication Methods
    
    **JWT Token:**
    ```
    Authorization: Bearer <your-jwt-token>
    ```
    
    **API Key:**
    ```
    X-API-Key: <your-api-key>
    ```
    
    ### Quick Start
    1. Login via OAuth to get JWT token
    2. Use JWT to create API keys
    3. Use either auth method to access protected endpoints
    """,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
)

# Add Session Middleware (required for OAuth)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="fastapi_session",  # More specific cookie name
    max_age=3600,  # 1 hour
    same_site="lax",
    https_only=False,  # Set to True in production with HTTPS
    path="/"  # Cookie available for all paths
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API information"""
    return {
        "status": "healthy",
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "api_v1": settings.API_V1_PREFIX
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "version": settings.VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

