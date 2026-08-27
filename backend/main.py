"""
FastAPI Application — Industrial Shell Data Retrieval, Casting Envelope & Quality Intelligence Portal.

Configures CORS, mounts static files for the frontend SPA,
and includes all API routers: Search, Documents, Analytics, Upload.
"""
import sys
from contextlib import asynccontextmanager
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.config import FRONTEND_DIR, DEBUG
from backend.routes.search import router as search_router
from backend.routes.documents import router as documents_router
from backend.routes.upload import router as upload_router
from backend.routes.analytics import router as analytics_router
from database.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables on startup."""
    init_db()
    yield


app = FastAPI(
    title="Qadri Group — Industrial Shell Data Retrieval, Casting Envelope & Quality Intelligence Portal",
    description="Qadri Group foundry shell retrieval, casting stock envelope calculator, defect analytics, and multi-year ingestion portal.",
    version="3.5.0",
    lifespan=lifespan,
)

# CORS — compliant with W3C / Fetch CORS specifications
if DEBUG:
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"^https?://.*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API routers
app.include_router(search_router)
app.include_router(documents_router)
app.include_router(upload_router)
app.include_router(analytics_router)

# Mount frontend static files
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/", include_in_schema=False)
@app.get("/search", include_in_schema=False)
def serve_index():
    """Serve the primary Dimensional Search & Machining Stock Envelope view."""
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/quality", include_in_schema=False)
@app.get("/analytics", include_in_schema=False)
def serve_quality():
    """Serve the Foundry Quality & Defect Intelligence Analytics page."""
    quality_file = FRONTEND_DIR / "quality.html"
    if quality_file.exists():
        return FileResponse(str(quality_file))
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/ingestion", include_in_schema=False)
@app.get("/upload-manager", include_in_schema=False)
def serve_ingestion():
    """Serve the Multi-Year Archive Ingestion Manager & Live Terminal page."""
    ingestion_file = FRONTEND_DIR / "ingestion.html"
    if ingestion_file.exists():
        return FileResponse(str(ingestion_file))
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/job-lookup", include_in_schema=False)
@app.get("/dossier", include_in_schema=False)
def serve_job_lookup():
    """Serve the dedicated Job Number Dossier & Document Download Center page."""
    job_file = FRONTEND_DIR / "job_lookup.html"
    if job_file.exists():
        return FileResponse(str(job_file))
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/health")
def health():
    return {"status": "ok", "service": "Qadri Group — Industrial Shell Portal v3.5"}


