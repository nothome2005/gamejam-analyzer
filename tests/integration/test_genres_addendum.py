"""
Integration tests for Addendum 02 (REQ-F-011): Project Genre Classification,
Catalog Filtering by Genre, and Global Genre Analytics.

Following strict TDD methodology:
This test suite is written prior to implementation changes to establish RED state.
"""

import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from src.api.app import app
from src.api.state import services

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_clean_state():
    """Ensure each test runs with a deterministic clean domain state."""
    services.reset()


def _seed_active_jam_and_team():
    """Helper to seed an active jam and registered team."""
    now = datetime.now(timezone.utc)
    # 1. Create Jam
    jam_payload = {
        "title": "Winter Indie Jam 2026",
        "theme": "Frozen Worlds",
        "start_time": (now + timedelta(days=1)).isoformat(),
        "submission_deadline": (now + timedelta(days=3)).isoformat(),
        "review_deadline": (now + timedelta(days=6)).isoformat(),
        "penalty_per_hour_percent": 5.0
    }
    jam_resp = client.post("/jams", json=jam_payload)
    assert jam_resp.status_code == 201
    jam_id = jam_resp.json()["id"]

    # Activate Jam
    status_resp = client.patch(f"/jams/{jam_id}/status", json={"status": "Active"})
    assert status_resp.status_code == 200

    # 2. Register Team
    team_payload = {
        "name": "PixelCrafters",
        "captain": {
            "user_id": "usr-captain-01",
            "name": "Andrii",
            "specialization": "Programmer"
        }
    }
    team_resp = client.post(f"/jams/{jam_id}/teams", json=team_payload)
    assert team_resp.status_code == 201
    team_id = team_resp.json()["id"]

    return jam_id, team_id


def test_tdd_genres_01_create_submission_with_valid_genres():
    """POS-GENRE-01: Submit project with valid genres list from taxonomy (AC-F-011.1)."""
    jam_id, team_id = _seed_active_jam_and_team()

    sub_payload = {
        "team_id": team_id,
        "title": "Frostbite Odyssey",
        "engine": "Godot 4.3",
        "git_url": "https://github.com/pixelcrafters/frostbite.git",
        "commit_hash": "a" * 40,
        "sha256_checksum": "b" * 64,
        "build_url": "https://itch.io/frostbite",
        "build_size_mb": 120.0,
        "genres": ["Platformer", "Puzzle"]
    }
    resp = client.post(f"/jams/{jam_id}/submissions", json=sub_payload)
    assert resp.status_code == 201
    data = resp.json()
    assert "genres" in data
    assert data["genres"] == ["Platformer", "Puzzle"]


def test_tdd_genres_02_create_submission_with_unknown_genre_fails():
    """NEG-GENRE-01: Reject submission with invalid genre outside taxonomy (AC-F-011.2)."""
    jam_id, team_id = _seed_active_jam_and_team()

    sub_payload = {
        "team_id": team_id,
        "title": "Frostbite Odyssey",
        "engine": "Godot 4.3",
        "git_url": "https://github.com/pixelcrafters/frostbite.git",
        "commit_hash": "a" * 40,
        "sha256_checksum": "b" * 64,
        "build_url": "https://itch.io/frostbite",
        "build_size_mb": 120.0,
        "genres": ["Platformer", "FakeUnknownGenreXYZ"]
    }
    resp = client.post(f"/jams/{jam_id}/submissions", json=sub_payload)
    assert resp.status_code == 422
    assert resp.headers.get("content-type") == "application/problem+json"
    problem = resp.json()
    assert problem["status"] == 422
    assert "genres" in str(problem)


def test_tdd_genres_03_create_submission_with_too_many_genres_fails():
    """NEG-GENRE-02: Reject submission with more than 3 genres (AC-F-011.2)."""
    jam_id, team_id = _seed_active_jam_and_team()

    sub_payload = {
        "team_id": team_id,
        "title": "Frostbite Odyssey",
        "engine": "Godot 4.3",
        "git_url": "https://github.com/pixelcrafters/frostbite.git",
        "commit_hash": "a" * 40,
        "sha256_checksum": "b" * 64,
        "build_url": "https://itch.io/frostbite",
        "build_size_mb": 120.0,
        "genres": ["Action", "Adventure", "Puzzle", "Platformer"]
    }
    resp = client.post(f"/jams/{jam_id}/submissions", json=sub_payload)
    assert resp.status_code == 422
    assert resp.headers.get("content-type") == "application/problem+json"


def test_tdd_genres_04_backward_compatibility_without_genres():
    """POS-GENRE-02: Ensure submission without genres field defaults safely to empty list (AC-F-011.6)."""
    jam_id, team_id = _seed_active_jam_and_team()

    sub_payload = {
        "team_id": team_id,
        "title": "Legacy Style Submission",
        "engine": "Godot 4.3",
        "git_url": "https://github.com/pixelcrafters/legacy.git",
        "commit_hash": "a" * 40,
        "sha256_checksum": "b" * 64,
        "build_url": "https://itch.io/legacy",
        "build_size_mb": 50.0
    }
    resp = client.post(f"/jams/{jam_id}/submissions", json=sub_payload)
    assert resp.status_code == 201
    data = resp.json()
    assert "genres" in data
    assert data["genres"] == []


def test_tdd_genres_05_update_submission_genres():
    """POS-GENRE-03: Update submission genres via PUT (AC-F-011.3)."""
    jam_id, team_id = _seed_active_jam_and_team()

    sub_payload = {
        "team_id": team_id,
        "title": "Frostbite Odyssey",
        "engine": "Godot 4.3",
        "git_url": "https://github.com/pixelcrafters/frostbite.git",
        "commit_hash": "a" * 40,
        "sha256_checksum": "b" * 64,
        "build_url": "https://itch.io/frostbite",
        "build_size_mb": 120.0,
        "genres": ["Platformer"]
    }
    create_resp = client.post(f"/jams/{jam_id}/submissions", json=sub_payload)
    assert create_resp.status_code == 201
    sub_id = create_resp.json()["id"]

    # Update genres
    update_resp = client.put(f"/submissions/{sub_id}", json={"genres": ["Roguelike", "Action"]})
    assert update_resp.status_code == 200
    updated_data = update_resp.json()
    assert updated_data["genres"] == ["Roguelike", "Action"]


def test_tdd_genres_06_filter_catalog_projects_by_genre():
    """POS-GENRE-04: Filter catalog projects by genre query param (AC-F-011.4)."""
    jam_id, team_id = _seed_active_jam_and_team()

    # Project 1: Platformer
    client.post(f"/jams/{jam_id}/submissions", json={
        "team_id": team_id,
        "title": "Platformer Game",
        "engine": "Godot 4.3",
        "git_url": "https://github.com/pixelcrafters/g1.git",
        "commit_hash": "a" * 40,
        "sha256_checksum": "b" * 64,
        "build_url": "https://itch.io/g1",
        "build_size_mb": 100.0,
        "genres": ["Platformer"]
    })

    # Complete the jam so projects appear in catalog
    client.patch(f"/jams/{jam_id}/status", json={"status": "Under Review"})
    client.patch(f"/jams/{jam_id}/status", json={"status": "Completed"})

    # Filter matching genre
    cat_resp = client.get("/catalog/projects?genre=Platformer")
    assert cat_resp.status_code == 200
    items = cat_resp.json()
    assert len(items) == 1
    assert items[0]["title"] == "Platformer Game"
    assert "Platformer" in items[0]["genres"]

    # Filter non-matching genre
    empty_resp = client.get("/catalog/projects?genre=Horror")
    assert empty_resp.status_code == 200
    assert empty_resp.json() == []


def test_tdd_genres_07_global_genre_analytics():
    """POS-GENRE-05: Aggregate global genre popularity statistics (AC-F-011.5)."""
    jam_id, team_id = _seed_active_jam_and_team()

    # Project 1: Platformer, Puzzle
    client.post(f"/jams/{jam_id}/submissions", json={
        "team_id": team_id,
        "title": "Game A",
        "engine": "Godot 4.3",
        "git_url": "https://github.com/pixelcrafters/ga.git",
        "commit_hash": "a" * 40,
        "sha256_checksum": "b" * 64,
        "build_url": "https://itch.io/ga",
        "build_size_mb": 100.0,
        "genres": ["Platformer", "Puzzle"]
    })

    resp = client.get("/analytics/genres")
    assert resp.status_code == 200
    stats = resp.json()
    assert isinstance(stats, list)
    assert len(stats) >= 2

    # Check Platformer presence
    platformer_stat = next((s for s in stats if s["genre"] == "Platformer"), None)
    assert platformer_stat is not None
    assert platformer_stat["count"] == 1
    assert platformer_stat["percentage"] == 100.0
