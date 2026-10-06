from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import db_manager

# Import API routers
from app.api.auth import router as auth_router
from app.api.incidents import router as incidents_router
from app.api.simulator import router as simulator_router
from app.api.knowledge import router as knowledge_router
from app.api.analysis import router as analysis_router
from app.api.postmortems import router as postmortems_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to MongoDB or activate educational in-memory fallback
    await db_manager.connect()
    yield
    # Shutdown: Close database connections
    await db_manager.disconnect()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Full-stack AI platform for Incident Investigation, Root Cause Analysis, RAG, and Postmortems.",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits localhost:5173, localhost:3000, and LAN devices
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check & System Status Endpoint
@app.get("/api/health")
async def health_check():
    db_status = "connected" if db_manager.is_connected_to_mongo else "in_memory_fallback"
    openai_configured = bool(settings.OPENAI_API_KEY and len(settings.OPENAI_API_KEY.strip()) > 5)
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": {
            "mode": db_status,
            "connected_to_mongo": db_manager.is_connected_to_mongo,
            "database_name": settings.DATABASE_NAME
        },
        "ai_engine": {
            "openai_configured": openai_configured,
            "chat_model": settings.OPENAI_MODEL,
            "embedding_model": settings.OPENAI_EMBEDDING_MODEL
        }
    }

# Register Feature Routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(incidents_router, prefix="/api/incidents", tags=["Incidents"])
app.include_router(simulator_router, prefix="/api/simulator", tags=["Incident Simulator"])
app.include_router(knowledge_router, prefix="/api/knowledge", tags=["RAG Knowledge Base"])
app.include_router(analysis_router, prefix="/api/analysis", tags=["AI Incident Analysis"])
app.include_router(postmortems_router, prefix="/api/postmortems", tags=["Postmortems"])

# Mount built frontend for unified cloud deployment (e.g. Render)
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

FRONTEND_DIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/dist"))
if os.path.exists(FRONTEND_DIST_DIR):
    assets_dir = os.path.join(FRONTEND_DIST_DIR, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Don't intercept undefined API calls
        if full_path.startswith("api"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="API route not found")
        file_path = os.path.join(FRONTEND_DIST_DIR, full_path)
        if full_path and os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(FRONTEND_DIST_DIR, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)

