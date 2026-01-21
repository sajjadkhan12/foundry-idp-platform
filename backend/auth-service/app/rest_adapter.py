"""
REST to gRPC adapter for auth microservice
This allows REST endpoints to call gRPC services
"""
import logging
# Configure logging to reduce verbosity
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.db_init import init_database
from app.config import settings
from app.routes import (
    auth,
    users,
    roles,
    groups,
    business_units,
    organizations,
    permissions,
    configurations,
)
from app.core.dependencies import PROTO_AVAILABLE

# App will be created with lifespan in the next block

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup: Initialize database
    try:
        await init_database()
    except Exception as e:
        import logging
        logging.error(f"Database initialization failed: {e}", exc_info=True)
        # Continue startup even if init fails
    
    yield
    # Shutdown (if needed)


# Create FastAPI app with lifespan
app = FastAPI(title="Auth Service REST Adapter", lifespan=lifespan)

# Add CORS middleware for browser compatibility (especially Chrome)
# Kong also handles CORS, but this ensures it works even if Kong is bypassed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Include routers
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1", tags=["Users"])
app.include_router(roles.router, prefix="/api/v1", tags=["Roles"])
app.include_router(groups.router, prefix="/api/v1", tags=["Groups"])
app.include_router(business_units.router, prefix="/api/v1", tags=["Business Units"])
app.include_router(organizations.router, prefix="/api/v1", tags=["Organizations"])
app.include_router(permissions.router, prefix="/api/v1", tags=["Permissions"])
app.include_router(configurations.router, prefix="/api/v1", tags=["Configurations"])

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "auth-microservice",
        "proto_ready": PROTO_AVAILABLE
    }

if __name__ == "__main__":
    import uvicorn
    # Make sure to run this file as module: python -m app.rest_adapter
    uvicorn.run(app, host="0.0.0.0", port=8000)
