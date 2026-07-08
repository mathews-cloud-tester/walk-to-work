"""
Shared fixtures for Walk to Work backend tests.
"""
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def client(tmp_path, monkeypatch):
    """FastAPI test client with isolated commute store."""
    from commute_store import CommuteStore
    import main

    main.commute_store = CommuteStore(tmp_path / "commute_walks.json")
    return TestClient(main.app)
