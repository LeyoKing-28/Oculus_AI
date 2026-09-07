from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database.database import engine, Base
from backend.database import models
from backend.api import events


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle context manager to create database tables on startup."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="AI-Powered Mobile Urban Intelligence Platform API",
    description="Backend API for receiving, persisting, and serving urban intelligence events captured by public transport fleets (SIH 2026 Problem Statement 26124).",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for future GIS frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include event API routes
app.include_router(events.router)


@app.get(
    "/",
    summary="Backend Health Check",
    description="Returns backend operational status and confirmation that API is online."
)
def root_health_check():
    """Root endpoint for backend health verification."""
    return {
        "status": "online",
        "message": "AI-Powered Mobile Urban Intelligence Platform API is running",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
