# -*- coding: utf-8 -*-
"""
Уніфіковані серіалізатори доменних сутностей у DTO-словники REST API.
Відокремлює логіку представлення даних (Presentation Layer) від контролерів маршрутизації.
"""

from src.jams.models import Jam
from src.teams.models import Team
from src.submissions.models import Submission
from src.evaluations.models import Evaluation

def serialize_jam(jam: Jam) -> dict:
    """Серіалізація картки джему у формат OpenAPI JamResponse."""
    return {
        "id": jam.id,
        "title": jam.title,
        "theme": jam.theme,
        "start_time": jam.start_time.isoformat() if hasattr(jam.start_time, "isoformat") else str(jam.start_time),
        "submission_deadline": jam.submission_deadline.isoformat() if hasattr(jam.submission_deadline, "isoformat") else str(jam.submission_deadline),
        "review_deadline": jam.review_deadline.isoformat() if hasattr(jam.review_deadline, "isoformat") else str(jam.review_deadline),
        "status": jam.status.value if hasattr(jam.status, "value") else str(jam.status),
        "penalty_per_hour_percent": jam.penalty_per_hour_percent
    }

def serialize_team(team: Team, invite_code: str = None) -> dict:
    """Серіалізація даних команди та списку спеціалізацій у TeamResponse."""
    members_data = []
    for m in team.members:
        members_data.append({
            "user_id": m.user_id,
            "name": getattr(m, "username", None) or getattr(m, "name", m.user_id),
            "username": getattr(m, "username", None) or getattr(m, "name", m.user_id),
            "specialization": m.specialization
        })
    code = invite_code or f"INV-{team.id.replace('team-', '')[:6].upper()}"
    return {
        "id": team.id,
        "name": team.name,
        "jam_id": team.jam_id,
        "captain_id": team.captain_id,
        "invite_code": code,
        "members": members_data
    }

def serialize_submission(sub: Submission) -> dict:
    """Серіалізація конкурсної роботи та аудиторських полів у SubmissionResponse."""
    return {
        "id": sub.id,
        "jam_id": sub.jam_id,
        "team_id": sub.team_id,
        "project_name": getattr(sub, "title", "Project"),
        "title": getattr(sub, "title", "Project"),
        "git_url": sub.git_url,
        "commit_hash": sub.commit_hash,
        "sha256_checksum": sub.sha256_checksum,
        "build_url": sub.build_url,
        "build_size_mb": sub.build_size_mb,
        "engine": sub.engine,
        "genres": getattr(sub, "genres", []) or [],
        "third_party_assets": getattr(sub, "asset_inventory", []),
        "asset_inventory": getattr(sub, "asset_inventory", []),
        "status": sub.status.value if hasattr(sub.status, "value") else str(sub.status),
        "submitted_at": sub.submitted_at.isoformat() if sub.submitted_at else None,
        "is_late": sub.is_late,
        "late_minutes": sub.late_minutes,
        "penalty_points": sub.penalty_points
    }

def serialize_catalog_project(sub: Submission) -> dict:
    """Серіалізація проєкту для публічного каталогу (OpenAPI CatalogProjectItem)."""
    return {
        "id": sub.id,
        "jam_id": sub.jam_id,
        "team_id": sub.team_id,
        "project_name": getattr(sub, "title", "Project"),
        "title": getattr(sub, "title", "Project"),
        "engine": sub.engine,
        "genres": getattr(sub, "genres", []) or [],
        "build_url": sub.build_url,
        "build_size_mb": sub.build_size_mb,
        "submitted_at": sub.submitted_at.isoformat() if sub.submitted_at else None
    }

def serialize_evaluation(ev: Evaluation) -> dict:
    """Серіалізація оцінки журі у EvaluationResponse."""
    return {
        "id": ev.id,
        "judge_id": ev.judge_id,
        "submission_id": ev.submission_id,
        "gameplay_score": ev.gameplay,
        "theme_score": ev.theme_relevance,
        "visual_score": ev.graphics,
        "audio_score": ev.audio,
        "weighted_average": ev.average_score,
        "average_score": ev.average_score,
        "feedback_comment": ev.comment
    }
