"""
Tests for commute walk store and distance helpers.
"""
from datetime import datetime, timedelta, timezone

import pytest

from commute_store import CommuteStore, haversine_meters, path_distance_meters
from models import (
    CommutePoint,
    CommuteSettings,
    CommuteWalkCreate,
    CommuteWalkUpdate,
)


@pytest.fixture
def store(tmp_path):
    return CommuteStore(tmp_path / "commute_walks.json")


class TestHaversine:
    def test_same_point_is_zero(self):
        assert haversine_meters(40.7, -74.0, 40.7, -74.0) == 0.0

    def test_known_short_distance(self):
        d = haversine_meters(40.0, -74.0, 40.001, -74.0)
        assert 100 < d < 130


class TestCommuteStore:
    def test_create_and_list_walk(self, store):
        walk = store.create_walk(
            CommuteWalkCreate(
                direction="to_work",
                points=[
                    CommutePoint(lat=40.7, lng=-74.0),
                    CommutePoint(lat=40.701, lng=-74.0),
                ],
            )
        )
        assert walk.id
        assert walk.status == "in_progress"
        assert walk.distance_meters > 0

        listed = store.list_walks()
        assert listed.total == 1
        assert listed.walks[0].id == walk.id

    def test_append_points_and_complete(self, store):
        walk = store.create_walk(CommuteWalkCreate(direction="to_home"))
        updated = store.append_points(
            walk.id,
            [
                CommutePoint(lat=40.7, lng=-74.0, recorded_at="2026-07-08T12:00:00+00:00"),
                CommutePoint(lat=40.702, lng=-74.001, recorded_at="2026-07-08T12:10:00+00:00"),
            ],
        )
        assert len(updated.points) == 2
        assert updated.distance_meters > 0

        finished = store.update_walk(
            walk.id,
            CommuteWalkUpdate(
                status="completed",
                ended_at="2026-07-08T12:20:00+00:00",
            ),
        )
        assert finished.status == "completed"
        assert finished.ended_at is not None
        assert finished.duration_seconds >= 0

    def test_delete_walk(self, store):
        walk = store.create_walk(CommuteWalkCreate())
        assert store.delete_walk(walk.id) is True
        assert store.get_walk(walk.id) is None
        assert store.delete_walk(walk.id) is False

    def test_settings_roundtrip(self, store):
        settings = CommuteSettings(
            home_label="Apt",
            work_label="Office",
            home_lat=40.7,
            home_lng=-74.0,
            work_lat=40.75,
            work_lng=-73.98,
        )
        saved = store.update_settings(settings)
        assert saved.home_label == "Apt"
        loaded = store.get_settings()
        assert loaded.work_label == "Office"
        assert loaded.home_lat == 40.7

    def test_stats_for_completed_walks(self, store):
        now = datetime.now(timezone.utc)
        for i in range(2):
            started = (now - timedelta(hours=i + 1)).isoformat()
            ended = (now - timedelta(hours=i)).isoformat()
            walk = store.create_walk(
                CommuteWalkCreate(
                    direction="to_work" if i == 0 else "to_home",
                    started_at=started,
                    points=[
                        CommutePoint(lat=40.7, lng=-74.0),
                        CommutePoint(lat=40.705, lng=-74.0),
                    ],
                )
            )
            store.update_walk(
                walk.id,
                CommuteWalkUpdate(status="completed", ended_at=ended),
            )

        stats = store.get_stats()
        assert stats.total_walks == 2
        assert stats.total_distance_meters > 0
        assert stats.walks_to_work == 1
        assert stats.walks_to_home == 1
        assert stats.current_streak_days >= 1

    def test_path_distance_empty(self):
        assert path_distance_meters([]) == 0.0
        assert path_distance_meters([CommutePoint(lat=1, lng=2)]) == 0.0
