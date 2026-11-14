# -*- coding: utf-8 -*-
"""
Submissions & Audit Verification Router (REQ-F-003, REQ-F-004, REQ-F-005, POS-04, POS-05, NEG-01, NEG-02).
"""

import re
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Header, Response, status
from pydantic import BaseModel, Field

from src.api.state import services
from src.api.errors import ProblemDetailsException
from src.api.middleware import log_system_event
from src.submissions.models import SubmissionCreate, Submission
from src.jams.models import JamStatus

router = APIRouter(tags=["Submissions"])

SHA256_PATTERN = re.compile(r"^[a-fA-F0-9]{64}$")

class SubmissionCreateDTO(BaseModel):
    team_id: str
    project_name: Optional[str] = None
    title: Optional[str] = None
    git_url: str
    commit_hash: str
    sha256_checksum: str
    build_size_mb: float
    engine: str
    build_url: Optional[str] = "https://builds.gamejam.local/download"
    third_party_assets: Optional[List[str]] = Field(default_factory=list)
    asset_inventory: Optional[List[str]] = None

class VerifyHashDTO(BaseModel):
    provided_sha256: str

def _submission_to_dict(sub: Submission) -> dict:
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
        "third_party_assets": getattr(sub, "asset_inventory", []),
        "asset_inventory": getattr(sub, "asset_inventory", []),
        "status": sub.status.value if hasattr(sub.status, "value") else str(sub.status),
        "submitted_at": sub.submitted_at.isoformat() if sub.submitted_at else None,
        "is_late": sub.is_late,
        "late_minutes": sub.late_minutes,
        "penalty_points": sub.penalty_points
    }

@router.post("/jams/{jam_id}/submissions", status_code=status.HTTP_201_CREATED, summary="Подання проєкту (REQ-F-003, REQ-F-004)")
def submit_project(jam_id: str, payload: SubmissionCreateDTO):
    jam = services.jam_service.get_jam(jam_id)
    if not jam:
        raise ProblemDetailsException(status=404, title="Not Found", detail=f"Джем '{jam_id}' не знайдено.")

    proj_name = payload.project_name or payload.title or "Untitled Jam Project"

    # Валідація SHA-256 (NEG-01: рівно 64 hex символи)
    if not SHA256_PATTERN.match(payload.sha256_checksum.strip()):
        raise ProblemDetailsException(
            status=422,
            title="Unprocessable Entity",
            detail="Поле 'sha256_checksum' повинно містити рівно 64 шістнадцяткові символи (SHA-256).",
            invalid_params=[{"name": "sha256_checksum", "reason": "Значення не відповідає регулярному виразу ^[a-fA-F0-9]{64}$"}]
        )

    # Валідація розміру білда (NEG-02: ліміт 500 МБ)
    if payload.build_size_mb > 500.0:
        raise ProblemDetailsException(
            status=422,
            title="Unprocessable Entity",
            detail=f"Розмір білда ({payload.build_size_mb} МБ) перевищує допустимий ліміт джему (500 МБ).",
            invalid_params=[{"name": "build_size_mb", "reason": "build_size_mb must be <= 500.0"}]
        )

    assets = payload.third_party_assets or payload.asset_inventory or []

    domain_create = SubmissionCreate(
        jam_id=jam_id,
        team_id=payload.team_id,
        title=proj_name,
        engine=payload.engine,
        git_url=payload.git_url,
        commit_hash=payload.commit_hash,
        sha256_checksum=payload.sha256_checksum.lower(),
        build_url=payload.build_url or "https://builds.gamejam.local/download",
        build_size_mb=payload.build_size_mb,
        asset_inventory=assets
    )

    submission = services.submission_service.submit_project(
        payload=domain_create,
        submission_deadline=jam.submission_deadline,
        review_deadline=jam.review_deadline,
        penalty_per_hour_percent=jam.penalty_per_hour_percent
    )

    # Аудит фіксації хешу та розміру білда (AC-NF-003)
    services.audit_logger.record_change(
        entity_type="Submission",
        entity_id=submission.id,
        field_name="sha256_checksum",
        old_value=None,
        new_value=submission.sha256_checksum,
        author_id=payload.team_id
    )

    # Додаємо до каталогу для доступності у публічному переліку
    services.catalog_service._submissions.append(submission)

    log_system_event("PROJECT_SUBMITTED", {
        "submission_id": submission.id,
        "jam_id": jam_id,
        "team_id": payload.team_id,
        "is_late": submission.is_late,
        "penalty_points": submission.penalty_points
    })

    return _submission_to_dict(submission)

@router.get("/jams/{jam_id}/submissions", summary="Список робіт джему")
def get_jam_submissions(jam_id: str, x_user_role: Optional[str] = Header("Guest", alias="X-User-Role")):
    jam = services.jam_service.get_jam(jam_id)
    if not jam:
        raise ProblemDetailsException(status=404, title="Not Found", detail=f"Джем '{jam_id}' не знайдено.")

    # Перевірка ізоляції в Under Review
    if jam.status == JamStatus.UNDER_REVIEW and x_user_role not in ("Judge", "Organizer", "Admin"):
        raise ProblemDetailsException(
            status=403,
            title="Forbidden",
            detail="Доступ до списку робіт закрито під час активного етапу суддівства Under Review."
        )

    subs = services.submission_service.list_submissions_by_jam(jam_id)
    return [_submission_to_dict(s) for s in subs]

@router.get("/submissions/{submission_id}", summary="Картка сабмішну")
def get_submission(submission_id: str, x_user_role: Optional[str] = Header("Guest", alias="X-User-Role")):
    sub = services.submission_service.get_submission(submission_id)
    if not sub:
        raise ProblemDetailsException(status=404, title="Not Found", detail=f"Сабмішн '{submission_id}' не знайдено.")

    jam = services.jam_service.get_jam(sub.jam_id)
    if jam and jam.status == JamStatus.UNDER_REVIEW:
        if x_user_role not in ("Judge", "Organizer", "Admin"):
            raise ProblemDetailsException(
                status=403,
                title="Forbidden",
                detail="Доступ до матеріалів проєкту обмежено на час закритого суддівства (Under Review)."
            )

    return _submission_to_dict(sub)

@router.post("/submissions/{submission_id}/verify-hash", summary="Верифікація цілісності білда за SHA-256")
def verify_submission_hash(submission_id: str, payload: VerifyHashDTO):
    sub = services.submission_service.get_submission(submission_id)
    if not sub:
        raise ProblemDetailsException(status=404, title="Not Found", detail=f"Сабмішн '{submission_id}' не знайдено.")

    provided = payload.provided_sha256.strip().lower()
    stored = sub.sha256_checksum.strip().lower()
    is_valid = (provided == stored)

    log_system_event("CHECKSUM_VERIFIED", {
        "submission_id": sub.id,
        "is_valid": is_valid,
        "provided": provided,
        "stored": stored
    })

    return {
        "submission_id": sub.id,
        "is_valid": is_valid,
        "git_commit_verified": is_valid,
        "expected_sha256": stored,
        "provided_sha256": provided,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
