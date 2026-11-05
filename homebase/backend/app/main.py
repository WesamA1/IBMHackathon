"""
WVU LCSEE Home Base — FastAPI Application

Startup order:
  1. Database tables created (or Alembic applies migrations).
  2. Seed data inserted if DB is empty.
  3. CORS middleware applied.
  4. All route modules mounted at /api/v1/.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .config import get_settings
from .database import engine, Base
from .routes import (
    updates_router, flashcards_router, tasks_router,
    events_router, gpa_router, resources_router,
)
from .seed import seed_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────────────
    Base.metadata.create_all(bind=engine)
    seed_db()
    yield
    # ── Shutdown ─────────────────────────────────────────────────────────
    # Nothing to clean up for SQLite; add connection-pool teardown here for PG.


app = FastAPI(
    title="WVU LCSEE Home Base API",
    description="Backend for the LCSEE student portal — updates, flashcards, tasks, planner, GPA, and resources.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routes ────────────────────────────────────────────────────────────────
PREFIX = "/api/v1"
app.include_router(updates_router,    prefix=PREFIX)
app.include_router(flashcards_router, prefix=PREFIX)
app.include_router(tasks_router,      prefix=PREFIX)
app.include_router(events_router,     prefix=PREFIX)
app.include_router(gpa_router,        prefix=PREFIX)
app.include_router(resources_router,  prefix=PREFIX)

# ── Serve frontend static files ───────────────────────────────────────────────
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "homebase-api"}
