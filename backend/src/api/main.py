from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .config import get_settings
from .db import engine, Base
# Import models so metadata has tables before create_all
from . import models  # noqa: F401
from .routers_patients import router as patients_router
from .routers_chat import router as chat_router

# Create DB tables if not exist (after importing models)
Base.metadata.create_all(bind=engine)

settings = get_settings()

openapi_tags = [
    {"name": "Root", "description": "Health check and root endpoints"},
    {"name": "Patients", "description": "Patient CRUD and history endpoints"},
    {"name": "Chat", "description": "Chat endpoints for dual-agent responses"},
]

app = FastAPI(
    title=settings.app_name,
    description=(
        "Backend API for AI Healthcare Assistant with dual agents "
        "(intake and recommendation)."
    ),
    version=settings.app_version,
    openapi_tags=openapi_tags,
)

# CORS configuration based on env
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# PUBLIC_INTERFACE
@app.get("/", tags=["Root"], summary="Health check")
def health_check():
    """Health check endpoint returning service status."""
    return {
        "message": "Healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "env": settings.environment,
    }


# Include routers
app.include_router(patients_router)
app.include_router(chat_router)


# PUBLIC_INTERFACE
@app.get(
    "/docs/websocket-help",
    tags=["Root"],
    summary="WebSocket usage note",
)
def websocket_usage_note():
    """Provide a note that real-time websockets are not implemented in this version."""
    return JSONResponse(
        {
            "message": (
                "WebSocket endpoints are not implemented in this version. "
                "Use REST endpoints under /patients and /chat."
            ),
            "rest_endpoints": ["/patients", "/patients/{id}/history", "/chat/send"],
        }
    )
