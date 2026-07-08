from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from typing import Optional

from models import (
    CommuteSettings,
    CommuteWalk,
    CommuteWalkCreate,
    CommuteWalkUpdate,
    CommutePointsAppend,
    CommuteWalkListResponse,
    CommuteStatsResponse,
)
from commute_store import CommuteStore

app = FastAPI(
    title="Walk to Work API",
    description="Track walking commutes between home and work",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

commute_path = Path(__file__).parent.parent / "data" / "commute_walks.json"
commute_store = CommuteStore(commute_path)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Walk to Work API",
        "endpoints": {
            "/api/commute/walks": "Track walk-to-work commute sessions",
            "/api/commute/stats": "Get commute walk statistics",
            "/api/commute/settings": "Get or update home/work locations",
            "/health": "Health check",
        },
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/commute/settings", response_model=CommuteSettings)
async def get_commute_settings():
    """Get home/work labels and optional coordinates."""
    return commute_store.get_settings()


@app.put("/api/commute/settings", response_model=CommuteSettings)
async def put_commute_settings(settings: CommuteSettings):
    """Update home/work labels and coordinates."""
    return commute_store.update_settings(settings)


@app.get("/api/commute/stats", response_model=CommuteStatsResponse)
async def get_commute_stats():
    """Aggregate stats for completed commute walks."""
    return commute_store.get_stats()


@app.get("/api/commute/walks", response_model=CommuteWalkListResponse)
async def list_commute_walks(
    limit: Optional[int] = Query(None, ge=1, le=200, description="Max walks to return"),
):
    """List commute walks, newest first."""
    return commute_store.list_walks(limit=limit)


@app.post("/api/commute/walks", response_model=CommuteWalk, status_code=201)
async def create_commute_walk(payload: CommuteWalkCreate):
    """Start a new walk-to-work (or home) session."""
    if payload.direction not in ("to_work", "to_home"):
        raise HTTPException(status_code=400, detail="direction must be to_work or to_home")
    return commute_store.create_walk(payload)


@app.get("/api/commute/walks/{walk_id}", response_model=CommuteWalk)
async def get_commute_walk(walk_id: str):
    """Get a single commute walk by id."""
    walk = commute_store.get_walk(walk_id)
    if walk is None:
        raise HTTPException(status_code=404, detail="Walk not found")
    return walk


@app.patch("/api/commute/walks/{walk_id}", response_model=CommuteWalk)
async def update_commute_walk(walk_id: str, payload: CommuteWalkUpdate):
    """Update walk status, notes, direction, or replace GPS points."""
    if payload.status is not None and payload.status not in (
        "in_progress",
        "completed",
        "cancelled",
    ):
        raise HTTPException(
            status_code=400,
            detail="status must be in_progress, completed, or cancelled",
        )
    if payload.direction is not None and payload.direction not in ("to_work", "to_home"):
        raise HTTPException(status_code=400, detail="direction must be to_work or to_home")
    walk = commute_store.update_walk(walk_id, payload)
    if walk is None:
        raise HTTPException(status_code=404, detail="Walk not found")
    return walk


@app.post("/api/commute/walks/{walk_id}/points", response_model=CommuteWalk)
async def append_commute_points(walk_id: str, payload: CommutePointsAppend):
    """Append GPS points to an in-progress walk."""
    if not payload.points:
        raise HTTPException(status_code=400, detail="points must not be empty")
    walk = commute_store.append_points(walk_id, payload.points)
    if walk is None:
        raise HTTPException(status_code=404, detail="Walk not found")
    return walk


@app.delete("/api/commute/walks/{walk_id}")
async def delete_commute_walk(walk_id: str):
    """Delete a commute walk."""
    if not commute_store.delete_walk(walk_id):
        raise HTTPException(status_code=404, detail="Walk not found")
    return {"ok": True, "id": walk_id}
