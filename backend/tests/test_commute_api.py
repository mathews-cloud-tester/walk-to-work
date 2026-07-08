"""
API tests for walk-to-work commute endpoints.
"""


class TestCommuteEndpoints:
    def test_settings_get_and_put(self, client):
        res = client.get("/api/commute/settings")
        assert res.status_code == 200
        assert res.json()["home_label"] == "959 Lombard St"
        assert res.json()["home_lat"] == 37.801945

        payload = {
            "home_label": "Brooklyn Apt",
            "work_label": "Office",
            "home_lat": 40.6782,
            "home_lng": -73.9442,
            "work_lat": 40.7128,
            "work_lng": -74.0060,
            "typical_distance_meters": 4500,
        }
        put = client.put("/api/commute/settings", json=payload)
        assert put.status_code == 200
        assert put.json()["home_label"] == "Brooklyn Apt"
        assert put.json()["typical_distance_meters"] == 4500

    def test_create_list_get_walk(self, client):
        create = client.post(
            "/api/commute/walks",
            json={
                "direction": "to_work",
                "points": [
                    {"lat": 40.6782, "lng": -73.9442},
                    {"lat": 40.68, "lng": -73.95},
                ],
            },
        )
        assert create.status_code == 201
        walk = create.json()
        assert walk["status"] == "in_progress"
        assert walk["distance_meters"] > 0

        listed = client.get("/api/commute/walks")
        assert listed.status_code == 200
        assert listed.json()["total"] == 1

        got = client.get(f"/api/commute/walks/{walk['id']}")
        assert got.status_code == 200
        assert got.json()["id"] == walk["id"]

    def test_append_points_and_complete(self, client):
        create = client.post(
            "/api/commute/walks",
            json={
                "direction": "to_home",
                "started_at": "2026-07-08T08:00:00+00:00",
                "points": [],
            },
        )
        walk_id = create.json()["id"]

        append = client.post(
            f"/api/commute/walks/{walk_id}/points",
            json={
                "points": [
                    {"lat": 40.7, "lng": -74.0, "recorded_at": "2026-07-08T08:00:00+00:00"},
                    {"lat": 40.701, "lng": -74.001, "recorded_at": "2026-07-08T08:05:00+00:00"},
                ]
            },
        )
        assert append.status_code == 200
        assert len(append.json()["points"]) == 2

        done = client.patch(
            f"/api/commute/walks/{walk_id}",
            json={"status": "completed", "ended_at": "2026-07-08T08:30:00+00:00"},
        )
        assert done.status_code == 200
        assert done.json()["status"] == "completed"
        assert done.json()["duration_seconds"] == 1800

        stats = client.get("/api/commute/stats")
        assert stats.status_code == 200
        assert stats.json()["total_walks"] == 1

    def test_invalid_direction(self, client):
        res = client.post(
            "/api/commute/walks",
            json={"direction": "sideways"},
        )
        assert res.status_code == 400

    def test_delete_walk(self, client):
        create = client.post("/api/commute/walks", json={"direction": "to_work"})
        walk_id = create.json()["id"]
        deleted = client.delete(f"/api/commute/walks/{walk_id}")
        assert deleted.status_code == 200
        missing = client.get(f"/api/commute/walks/{walk_id}")
        assert missing.status_code == 404

    def test_root_and_health(self, client):
        res = client.get("/")
        assert res.status_code == 200
        assert "/api/commute/walks" in res.json()["endpoints"]

        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["status"] == "ok"
