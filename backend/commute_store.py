"""
JSON-backed store for walk-to-work commute sessions.
"""
from __future__ import annotations

import json
import math
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from models import (
    CommutePoint,
    CommuteSettings,
    CommuteStatsResponse,
    CommuteWalk,
    CommuteWalkCreate,
    CommuteWalkListResponse,
    CommuteWalkUpdate,
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two WGS84 points in meters."""
    r = 6_371_000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return 2 * r * math.asin(math.sqrt(a))


def path_distance_meters(points: list[CommutePoint]) -> float:
    if len(points) < 2:
        return 0.0
    total = 0.0
    for i in range(1, len(points)):
        prev, curr = points[i - 1], points[i]
        total += haversine_meters(prev.lat, prev.lng, curr.lat, curr.lng)
    return total


class CommuteStore:
    """Persist commute walks and settings to a JSON file."""

    def __init__(self, storage_path: str | Path):
        self.path = Path(storage_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_file()

    def _ensure_file(self) -> None:
        if not self.path.exists():
            self._write({"walks": [], "settings": CommuteSettings().model_dump()})

    def _read(self) -> dict:
        self._ensure_file()
        with self.path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("walks", [])
        data.setdefault("settings", CommuteSettings().model_dump())
        return data

    def _write(self, data: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        tmp.replace(self.path)

    def get_settings(self) -> CommuteSettings:
        return CommuteSettings(**self._read()["settings"])

    def update_settings(self, settings: CommuteSettings) -> CommuteSettings:
        data = self._read()
        data["settings"] = settings.model_dump()
        self._write(data)
        return settings

    def list_walks(self, limit: Optional[int] = None) -> CommuteWalkListResponse:
        walks = [CommuteWalk(**w) for w in self._read()["walks"]]
        walks.sort(key=lambda w: w.started_at, reverse=True)
        total = len(walks)
        if limit is not None:
            walks = walks[:limit]
        return CommuteWalkListResponse(walks=walks, total=total)

    def get_walk(self, walk_id: str) -> Optional[CommuteWalk]:
        for walk in self._read()["walks"]:
            if walk["id"] == walk_id:
                return CommuteWalk(**walk)
        return None

    def create_walk(self, payload: CommuteWalkCreate) -> CommuteWalk:
        points = list(payload.points)
        distance = path_distance_meters(points)
        walk = CommuteWalk(
            id=str(uuid.uuid4()),
            started_at=payload.started_at or _utc_now_iso(),
            ended_at=None,
            status="in_progress",
            direction=payload.direction,
            notes=payload.notes,
            points=points,
            distance_meters=round(distance, 2),
            duration_seconds=0,
        )
        data = self._read()
        data["walks"].append(walk.model_dump())
        self._write(data)
        return walk

    def update_walk(self, walk_id: str, payload: CommuteWalkUpdate) -> Optional[CommuteWalk]:
        data = self._read()
        for i, raw in enumerate(data["walks"]):
            if raw["id"] != walk_id:
                continue
            walk = CommuteWalk(**raw)

            if payload.points is not None:
                walk.points = list(payload.points)
            if payload.notes is not None:
                walk.notes = payload.notes
            if payload.direction is not None:
                walk.direction = payload.direction
            if payload.status is not None:
                walk.status = payload.status

            walk.distance_meters = round(path_distance_meters(walk.points), 2)

            if walk.status == "completed":
                walk.ended_at = payload.ended_at or walk.ended_at or _utc_now_iso()
                try:
                    start = datetime.fromisoformat(walk.started_at)
                    end = datetime.fromisoformat(walk.ended_at)
                    walk.duration_seconds = max(0, int((end - start).total_seconds()))
                except ValueError:
                    walk.duration_seconds = 0
            elif walk.status == "cancelled":
                walk.ended_at = payload.ended_at or walk.ended_at or _utc_now_iso()
                walk.duration_seconds = 0

            data["walks"][i] = walk.model_dump()
            self._write(data)
            return walk
        return None

    def append_points(self, walk_id: str, points: list[CommutePoint]) -> Optional[CommuteWalk]:
        data = self._read()
        for i, raw in enumerate(data["walks"]):
            if raw["id"] != walk_id:
                continue
            walk = CommuteWalk(**raw)
            if walk.status != "in_progress":
                return walk
            walk.points.extend(points)
            walk.distance_meters = round(path_distance_meters(walk.points), 2)
            data["walks"][i] = walk.model_dump()
            self._write(data)
            return walk
        return None

    def delete_walk(self, walk_id: str) -> bool:
        data = self._read()
        before = len(data["walks"])
        data["walks"] = [w for w in data["walks"] if w["id"] != walk_id]
        if len(data["walks"]) == before:
            return False
        self._write(data)
        return True

    def get_stats(self) -> CommuteStatsResponse:
        walks = [CommuteWalk(**w) for w in self._read()["walks"]]
        completed = [w for w in walks if w.status == "completed"]
        total_distance = sum(w.distance_meters for w in completed)
        total_duration = sum(w.duration_seconds for w in completed)
        count = len(completed)
        avg_distance = (total_distance / count) if count else 0.0
        avg_duration = (total_duration / count) if count else 0.0

        # Current streak: consecutive calendar days (UTC) with a completed walk
        from datetime import timedelta

        day_set = {
            datetime.fromisoformat(w.started_at).date()
            for w in completed
            if w.started_at
        }
        streak = 0
        if day_set:
            today = datetime.now(timezone.utc).date()
            cursor = today if today in day_set else today - timedelta(days=1)
            if cursor in day_set:
                while cursor in day_set:
                    streak += 1
                    cursor -= timedelta(days=1)

        to_work = sum(1 for w in completed if w.direction == "to_work")
        to_home = sum(1 for w in completed if w.direction == "to_home")

        return CommuteStatsResponse(
            total_walks=count,
            total_distance_meters=round(total_distance, 2),
            total_duration_seconds=total_duration,
            average_distance_meters=round(avg_distance, 2),
            average_duration_seconds=round(avg_duration, 1),
            current_streak_days=streak,
            walks_to_work=to_work,
            walks_to_home=to_home,
        )
