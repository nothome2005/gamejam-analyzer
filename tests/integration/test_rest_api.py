# -*- coding: utf-8 -*-
"""
Контрактний тест-сьют для перевірки реальної серверної реалізації REST API (FastAPI).
Розроблено відповідно до затвердженої специфікації OpenAPI 3.0.3 (docs/openapi.yaml),
SRS v1.0 (spec/srs.md) та сценаріїв перевірки API-GATE.

Методологія: TDD (Test-Driven Development) - фаза RED (створення до коду).
"""

import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

# Примітка TDD: імпорт серверного додатку, який має бути створений на етапі реалізації
from src.api.app import app

@pytest.fixture
def client():
    """Фікстура HTTP-клієнта для взаємодії з REST API додатком."""
    return TestClient(app)

# ============================================================================
# ПОЗИТИВНІ СЦЕНАРІЇ (POSITIVE SCENARIOS: POS-01 .. POS-09)
# ============================================================================

def test_sys_01_health_check(client):
    """SYS-01: Діагностика стану сервера та UTC часу."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data

def test_pos_01_create_jam(client):
    """POS-01 / REQ-F-001: Створення нового джему та конфігурація часових меж."""
    now = datetime.now(timezone.utc)
    payload = {
        "title": "Winter Indie Jam 2026",
        "theme": "Isolation and Discovery",
        "start_time": (now + timedelta(days=1)).isoformat(),
        "submission_deadline": (now + timedelta(days=3)).isoformat(),
        "review_deadline": (now + timedelta(days=6)).isoformat(),
        "penalty_per_hour_percent": 5.0
    }
    response = client.post("/jams", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["status"] == "Draft" or data["status"] == "Active"
    assert "id" in data

def test_pos_02_list_jams_with_filter(client):
    """POS-02 / REQ-F-001: Отримання списку джемів із фільтрацією за статусом."""
    # Спочатку гарантуємо наявність джему
    now = datetime.now(timezone.utc)
    payload = {
        "title": "Cyber Jam 2026",
        "theme": "Neon Lights",
        "start_time": (now + timedelta(days=1)).isoformat(),
        "submission_deadline": (now + timedelta(days=2)).isoformat(),
        "review_deadline": (now + timedelta(days=3)).isoformat(),
        "penalty_per_hour_percent": 3.0
    }
    create_res = client.post("/jams", json=payload)
    assert create_res.status_code == 201
    jam_id = create_res.json()["id"]

    response = client.get("/jams")
    assert response.status_code == 200
    jams = response.json()
    assert isinstance(jams, list)
    assert any(j["id"] == jam_id for j in jams)

def test_pos_03_team_registration_and_invite_flow(client):
    """POS-03 / REQ-F-002: Реєстрація команди, інвайт-код та приєднання учасника."""
    # Створюємо джем для команди
    now = datetime.now(timezone.utc)
    jam_res = client.post("/jams", json={
        "title": "Team Battle Jam",
        "theme": "Cooperation",
        "start_time": now.isoformat(),
        "submission_deadline": (now + timedelta(days=2)).isoformat(),
        "review_deadline": (now + timedelta(days=4)).isoformat()
    })
    jam_id = jam_res.json()["id"]

    # 1. Реєстрація команди капітаном
    team_payload = {
        "name": "Pixel Knights",
        "captain": {
            "user_id": "usr-captain-01",
            "name": "Oleksandr",
            "specialization": "Programmer"
        }
    }
    team_res = client.post(f"/jams/{jam_id}/teams", json=team_payload)
    assert team_res.status_code == 201
    team_data = team_res.json()
    team_id = team_data["id"]
    invite_code = team_data.get("invite_code")
    assert invite_code is not None

    # 2. Перевірка команди через GET /teams/{id}
    get_res = client.get(f"/teams/{team_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Pixel Knights"

    # 3. Приєднання нового учасника за інвайт-кодом
    join_payload = {
        "invite_code": invite_code,
        "member": {
            "user_id": "usr-artist-02",
            "name": "Maria",
            "specialization": "Artist"
        }
    }
    join_res = client.post(f"/teams/{team_id}/members", json=join_payload)
    assert join_res.status_code == 200
    assert len(join_res.json()["members"]) == 2

def test_pos_04_submit_project_with_checksum(client):
    """POS-04 / REQ-F-003, REQ-F-004, REQ-F-005: Подання проєкту із 64-hex SHA-256."""
    now = datetime.now(timezone.utc)
    jam_res = client.post("/jams", json={
        "title": "Godot Speed Jam",
        "theme": "Speed",
        "start_time": now.isoformat(),
        "submission_deadline": (now + timedelta(hours=48)).isoformat(),
        "review_deadline": (now + timedelta(hours=72)).isoformat()
    })
    jam_id = jam_res.json()["id"]

    team_res = client.post(f"/jams/{jam_id}/teams", json={
        "name": "Fast Devs",
        "captain": {"user_id": "usr-fast-01", "name": "Ivan", "specialization": "Programmer"}
    })
    team_id = team_res.json()["id"]

    sub_payload = {
        "team_id": team_id,
        "project_name": "Sonic Echoes",
        "git_url": "https://github.com/fastdevs/sonic-echoes.git",
        "commit_hash": "e4d909c290d0fb1ca068ffaddf22cbd0add81234",
        "sha256_checksum": "a" * 64,
        "build_size_mb": 145.5,
        "engine": "Godot",
        "third_party_assets": ["Kenney Audio Kit"]
    }
    sub_res = client.post(f"/jams/{jam_id}/submissions", json=sub_payload)
    assert sub_res.status_code == 201
    sub_data = sub_res.json()
    assert sub_data["project_name"] == "Sonic Echoes"
    assert sub_data["sha256_checksum"] == "a" * 64
    assert sub_data["is_late"] is False
    assert sub_data["penalty_points"] == 0.0

def test_pos_05_verify_checksum(client):
    """POS-05 / REQ-F-003: Криптографічна верифікація цілісності білда за SHA-256."""
    now = datetime.now(timezone.utc)
    jam_res = client.post("/jams", json={
        "title": "Crypto Jam",
        "theme": "Security",
        "start_time": now.isoformat(),
        "submission_deadline": (now + timedelta(days=2)).isoformat(),
        "review_deadline": (now + timedelta(days=4)).isoformat()
    })
    jam_id = jam_res.json()["id"]

    team_res = client.post(f"/jams/{jam_id}/teams", json={
        "name": "Hashers",
        "captain": {"user_id": "usr-hash-01", "name": "Bohdan", "specialization": "Programmer"}
    })
    team_id = team_res.json()["id"]

    sha_val = "1234567890abcdef" * 4
    sub_res = client.post(f"/jams/{jam_id}/submissions", json={
        "team_id": team_id,
        "project_name": "Secure Lock",
        "git_url": "https://github.com/hashers/lock.git",
        "commit_hash": "abcdef1234567890abcdef1234567890abcdef12",
        "sha256_checksum": sha_val,
        "build_size_mb": 50.0,
        "engine": "Unity"
    })
    sub_id = sub_res.json()["id"]

    verify_res = client.post(f"/submissions/{sub_id}/verify-hash", json={
        "provided_sha256": sha_val
    })
    assert verify_res.status_code == 200
    vdata = verify_res.json()
    assert vdata["is_valid"] is True
    assert vdata["git_commit_verified"] is True

def test_pos_06_and_07_evaluations_and_leaderboard(client):
    """POS-06, POS-07 / REQ-F-007, REQ-F-008: Оцінювання журі за 5 критеріями та формування лідерборду."""
    now = datetime.now(timezone.utc)
    jam_res = client.post("/jams", json={
        "title": "Award Jam",
        "theme": "Stars",
        "start_time": now.isoformat(),
        "submission_deadline": (now + timedelta(days=1)).isoformat(),
        "review_deadline": (now + timedelta(days=3)).isoformat()
    })
    jam_id = jam_res.json()["id"]

    team_res = client.post(f"/jams/{jam_id}/teams", json={
        "name": "Award Team",
        "captain": {"user_id": "usr-award-01", "name": "Stepan", "specialization": "Programmer"}
    })
    team_id = team_res.json()["id"]

    sub_res = client.post(f"/jams/{jam_id}/submissions", json={
        "team_id": team_id,
        "project_name": "Star Dust",
        "git_url": "https://github.com/award/stardust.git",
        "commit_hash": "f" * 40,
        "sha256_checksum": "b" * 64,
        "build_size_mb": 80.0,
        "engine": "Godot"
    })
    sub_id = sub_res.json()["id"]

    # Додаємо оцінку журі (5 критеріїв від 1 до 5)
    eval_payload = {
        "judge_id": "judge-expert-01",
        "gameplay_score": 5,
        "theme_score": 4,
        "originality_score": 5,
        "visual_score": 4,
        "audio_score": 3,
        "feedback_comment": "Чудова механіка та гарний саундтрек!"
    }
    eval_res = client.post(f"/submissions/{sub_id}/evaluations", json=eval_payload)
    assert eval_res.status_code == 201
    edata = eval_res.json()
    assert edata["weighted_average"] == pytest.approx(4.25, 0.1)

    # Отримуємо лідерборд джему
    lead_res = client.get(f"/jams/{jam_id}/leaderboard")
    assert lead_res.status_code == 200
    lb = lead_res.json()
    assert len(lb) >= 1
    assert lb[0]["project_name"] == "Star Dust"
    assert lb[0]["final_score"] > 0

def test_pos_08_and_09_analytics_and_catalog(client):
    """POS-08, POS-09 / REQ-F-009, REQ-F-010: Статистика використання рушіїв та каталог проєктів."""
    # Перевірка глобальної аналітики рушіїв
    eng_res = client.get("/analytics/engines")
    assert eng_res.status_code == 200
    stats = eng_res.json()
    assert isinstance(stats, list)

    # Перевірка публічного каталогу проєктів
    cat_res = client.get("/catalog/projects?engine=Godot")
    assert cat_res.status_code == 200
    projects = cat_res.json()
    assert isinstance(projects, list)

# ============================================================================
# НЕГАТИВНІ СЦЕНАРІЇ ТА RFC 7807 PROBLEM DETAILS (NEG-01 .. NEG-06)
# ============================================================================

def test_neg_01_invalid_sha256_format(client):
    """NEG-01 / REQ-F-003: Невалідний формат хешу SHA-256 (не 64 hex символи) -> 422 Problem Details."""
    now = datetime.now(timezone.utc)
    jam_res = client.post("/jams", json={
        "title": "Val Jam",
        "theme": "Strict",
        "start_time": now.isoformat(),
        "submission_deadline": (now + timedelta(days=2)).isoformat(),
        "review_deadline": (now + timedelta(days=4)).isoformat()
    })
    jam_id = jam_res.json()["id"]

    team_res = client.post(f"/jams/{jam_id}/teams", json={
        "name": "Val Team",
        "captain": {"user_id": "usr-val-01", "name": "Val", "specialization": "Programmer"}
    })
    team_id = team_res.json()["id"]

    bad_sub = {
        "team_id": team_id,
        "project_name": "Broken Hash Game",
        "git_url": "https://github.com/val/broken.git",
        "commit_hash": "f" * 40,
        "sha256_checksum": "INVALID_NOT_HEX_SHORT",
        "build_size_mb": 100.0,
        "engine": "Godot"
    }
    response = client.post(f"/jams/{jam_id}/submissions", json=bad_sub)
    assert response.status_code == 422
    assert response.headers.get("content-type", "").startswith("application/problem+json")
    prob = response.json()
    assert prob["status"] == 422
    assert "sha256_checksum" in str(prob)

def test_neg_02_build_size_exceeded(client):
    """NEG-02 / REQ-F-004: Перевищення ліміту розміру білда (> 500 MB) -> 422 Problem Details."""
    now = datetime.now(timezone.utc)
    jam_res = client.post("/jams", json={
        "title": "Limit Jam",
        "theme": "Heavy",
        "start_time": now.isoformat(),
        "submission_deadline": (now + timedelta(days=2)).isoformat(),
        "review_deadline": (now + timedelta(days=4)).isoformat()
    })
    jam_id = jam_res.json()["id"]

    team_res = client.post(f"/jams/{jam_id}/teams", json={
        "name": "Heavy Team",
        "captain": {"user_id": "usr-heavy-01", "name": "Heavy", "specialization": "Programmer"}
    })
    team_id = team_res.json()["id"]

    huge_sub = {
        "team_id": team_id,
        "project_name": "Massive Game",
        "git_url": "https://github.com/heavy/massive.git",
        "commit_hash": "f" * 40,
        "sha256_checksum": "c" * 64,
        "build_size_mb": 650.0,  # Більше ніж дозволені 500 МБ
        "engine": "Unreal"
    }
    response = client.post(f"/jams/{jam_id}/submissions", json=huge_sub)
    assert response.status_code == 422
    assert response.headers.get("content-type", "").startswith("application/problem+json")
    prob = response.json()
    assert prob["status"] == 422
    assert "build_size_mb" in str(prob) or "500" in str(prob)

def test_neg_03_score_out_of_bounds(client):
    """NEG-03 / REQ-F-007: Бал оцінки судді поза допустимим діапазоном 1-5 (бал 6) -> 422."""
    now = datetime.now(timezone.utc)
    jam_res = client.post("/jams", json={
        "title": "Judge Jam",
        "theme": "Scoring",
        "start_time": now.isoformat(),
        "submission_deadline": (now + timedelta(days=1)).isoformat(),
        "review_deadline": (now + timedelta(days=3)).isoformat()
    })
    jam_id = jam_res.json()["id"]

    team_res = client.post(f"/jams/{jam_id}/teams", json={
        "name": "Score Team",
        "captain": {"user_id": "usr-sc-01", "name": "Sc", "specialization": "Programmer"}
    })
    team_id = team_res.json()["id"]

    sub_res = client.post(f"/jams/{jam_id}/submissions", json={
        "team_id": team_id,
        "project_name": "Score Project",
        "git_url": "https://github.com/sc/proj.git",
        "commit_hash": "f" * 40,
        "sha256_checksum": "d" * 64,
        "build_size_mb": 10.0,
        "engine": "Godot"
    })
    sub_id = sub_res.json()["id"]

    bad_eval = {
        "judge_id": "judge-02",
        "gameplay_score": 6,  # Невалідне значення > 5
        "theme_score": 5,
        "originality_score": 5,
        "visual_score": 5,
        "audio_score": 5
    }
    response = client.post(f"/submissions/{sub_id}/evaluations", json=bad_eval)
    assert response.status_code == 422
    assert response.headers.get("content-type", "").startswith("application/problem+json")

def test_neg_04_access_evaluations_under_review_forbidden(client):
    """NEG-04 / REQ-F-006, REQ-NF-002: Спроба публічного доступу до оцінок під час Under Review -> 403."""
    now = datetime.now(timezone.utc)
    jam_res = client.post("/jams", json={
        "title": "Secret Jam",
        "theme": "Mystery",
        "start_time": now.isoformat(),
        "submission_deadline": (now + timedelta(days=1)).isoformat(),
        "review_deadline": (now + timedelta(days=3)).isoformat()
    })
    jam_id = jam_res.json()["id"]

    # Переводимо джем у стан UnderReview
    client.patch(f"/jams/{jam_id}/status", json={"status": "UnderReview"})

    team_res = client.post(f"/jams/{jam_id}/teams", json={
        "name": "Secret Team",
        "captain": {"user_id": "usr-sec-01", "name": "Sec", "specialization": "Programmer"}
    })
    team_id = team_res.json()["id"]

    sub_res = client.post(f"/jams/{jam_id}/submissions", json={
        "team_id": team_id,
        "project_name": "Secret Project",
        "git_url": "https://github.com/sec/proj.git",
        "commit_hash": "a" * 40,
        "sha256_checksum": "e" * 64,
        "build_size_mb": 25.0,
        "engine": "Custom"
    })
    sub_id = sub_res.json()["id"]

    # Звичайний учасник робить запит без заголовка судді
    response = client.get(f"/submissions/{sub_id}/evaluations", headers={"X-User-Role": "Participant"})
    assert response.status_code == 403
    assert response.headers.get("content-type", "").startswith("application/problem+json")
    prob = response.json()
    assert prob["status"] == 403

def test_neg_05_resource_not_found(client):
    """NEG-05 / RFC 7807: Запит неіснуючого ідентифікатора джему -> 404 Problem Details."""
    response = client.get("/jams/jam-non-existent-999")
    assert response.status_code == 404
    assert response.headers.get("content-type", "").startswith("application/problem+json")
    prob = response.json()
    assert prob["status"] == 404
    assert "Not Found" in prob["title"]

def test_neg_06_team_membership_conflict(client):
    """NEG-06 / REQ-F-002: Спроба користувача перебувати у кількох командах одного джему -> 409 Conflict."""
    now = datetime.now(timezone.utc)
    jam_res = client.post("/jams", json={
        "title": "Solo-Team Jam",
        "theme": "Loyalty",
        "start_time": now.isoformat(),
        "submission_deadline": (now + timedelta(days=2)).isoformat(),
        "review_deadline": (now + timedelta(days=4)).isoformat()
    })
    jam_id = jam_res.json()["id"]

    # Створюємо першу команду з користувачем usr-duplicate-99
    client.post(f"/jams/{jam_id}/teams", json={
        "name": "Team One",
        "captain": {"user_id": "usr-duplicate-99", "name": "Duplicate User", "specialization": "Programmer"}
    })

    # Спроба створити другу команду з тим самим капітаном у тому ж джемі
    conflict_res = client.post(f"/jams/{jam_id}/teams", json={
        "name": "Team Two",
        "captain": {"user_id": "usr-duplicate-99", "name": "Duplicate User", "specialization": "Artist"}
    })
    assert conflict_res.status_code == 409
    assert conflict_res.headers.get("content-type", "").startswith("application/problem+json")
    prob = conflict_res.json()
    assert prob["status"] == 409
    assert "Conflict" in prob["title"]
