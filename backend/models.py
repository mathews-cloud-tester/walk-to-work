from pydantic import BaseModel
from typing import Optional

class CommutePoint(BaseModel):
    lat: float
    lng: float
    recorded_at: Optional[str] = None
    accuracy_meters: Optional[float] = None


class CommuteSettings(BaseModel):
    home_label: str = "Home"
    work_label: str = "Work"
    home_lat: Optional[float] = None
    home_lng: Optional[float] = None
    work_lat: Optional[float] = None
    work_lng: Optional[float] = None
    typical_distance_meters: Optional[float] = None


class CommuteWalk(BaseModel):
    id: str
    started_at: str
    ended_at: Optional[str] = None
    status: str = "in_progress"  # in_progress | completed | cancelled
    direction: str = "to_work"  # to_work | to_home
    notes: Optional[str] = None
    points: list[CommutePoint] = []
    distance_meters: float = 0.0
    duration_seconds: int = 0


class CommuteWalkCreate(BaseModel):
    direction: str = "to_work"
    notes: Optional[str] = None
    started_at: Optional[str] = None
    points: list[CommutePoint] = []


class CommuteWalkUpdate(BaseModel):
    status: Optional[str] = None
    direction: Optional[str] = None
    notes: Optional[str] = None
    ended_at: Optional[str] = None
    points: Optional[list[CommutePoint]] = None


class CommutePointsAppend(BaseModel):
    points: list[CommutePoint]


class CommuteWalkListResponse(BaseModel):
    walks: list[CommuteWalk]
    total: int


class CommuteStatsResponse(BaseModel):
    total_walks: int
    total_distance_meters: float
    total_duration_seconds: int
    average_distance_meters: float
    average_duration_seconds: float
    current_streak_days: int
    walks_to_work: int
    walks_to_home: int

