# -*- coding: utf-8 -*-
"""
Jams Management Router (REQ-F-001, AC-F-001, BDD-SC-001).
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Query, Response, status
from pydantic import BaseModel, Field

from src.api.state import services
from src.api.errors import ProblemDetailsException
from src.api.middleware import log_system_event
from src.jams.models import JamCreate, JamStatus

router = APIRouter(prefix="/jams", tags=["Jams"])

class JamCreateDTO(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    theme: str = Field(..., min_length=1, max_length=200)
    start_time: datetime
    submission_deadline: datetime
    review_deadline: datetime
    penalty_per_hour_percent: float = Field(default=5.0, ge=0.0, le=100.0)

class JamStatusUpdateDTO(BaseModel):
    status: str

def _jam_to_dict(jam) -> dict:
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

@router.post("", status_code=status.HTTP_201_CREATED, summary="Створення джему (REQ-F-001)")
def create_jam(payload: JamCreateDTO):
    # Валідація хронології дедлайнів
    if payload.start_time >= payload.submission_deadline:
        raise ProblemDetailsException(
            status=422,
            title="Unprocessable Entity",
            detail="Час початку (start_time) повинен бути раніше за дедлайн подання робіт.",
            invalid_params=[{"name": "submission_deadline", "reason": "submission_deadline must be after start_time"}]
        )
    if payload.submission_deadline >= payload.review_deadline:
        raise ProblemDetailsException(
            status=422,
            title="Unprocessable Entity",
            detail="Дедлайн подання повинен бути раніше за дедлайн оцінювання.",
            invalid_params=[{"name": "review_deadline", "reason": "review_deadline must be after submission_deadline"}]
        )

    domain_payload = JamCreate(
        title=payload.title,
        theme=payload.theme,
        start_time=payload.start_time,
        submission_deadline=payload.submission_deadline,
        review_deadline=payload.review_deadline,
        penalty_per_hour_percent=payload.penalty_per_hour_percent
    )
    jam = services.jam_service.create_jam(domain_payload)
    
    log_system_event("JAM_CREATED", {"jam_id": jam.id, "title": jam.title})
    return _jam_to_dict(jam)

@router.get("", summary="Отримання списку джемів із фільтром")
def list_jams(status: Optional[str] = Query(None)):
    all_jams = list(services.jam_service._jams.values())
    if status:
        filtered = [j for j in all_jams if (j.status.value if hasattr(j.status, "value") else str(j.status)).lower() == status.lower()]
    else:
        filtered = all_jams
    return [_jam_to_dict(j) for j in filtered]

@router.get("/{jam_id}", summary="Отримання картки джему")
def get_jam(jam_id: str):
    jam = services.jam_service.get_jam(jam_id)
    if not jam:
        raise ProblemDetailsException(
            status=404,
            title="Not Found",
            detail=f"Джем із вказаним ідентифікатором '{jam_id}' не знайдено."
        )
    return _jam_to_dict(jam)

@router.patch("/{jam_id}/status", summary="Переведення фази джему (State Machine)")
def update_jam_status(jam_id: str, payload: JamStatusUpdateDTO):
    jam = services.jam_service.get_jam(jam_id)
    if not jam:
        raise ProblemDetailsException(
            status=404,
            title="Not Found",
            detail=f"Джем із вказаним ідентифікатором '{jam_id}' не знайдено."
        )

    new_status = payload.status
    # Оновлення статусу джему
    valid_statuses = ["Draft", "Created", "Active", "SubmissionClosed", "UnderReview", "Under Review", "Completed", "Complete"]
    if new_status not in valid_statuses:
        raise ProblemDetailsException(
            status=422,
            title="Unprocessable Entity",
            detail=f"Недопустимий статус джему: '{new_status}'."
        )

    # Присвоюємо нормалізований статус
    if new_status in ("UnderReview", "Under Review"):
        jam.status = JamStatus.UNDER_REVIEW
    elif new_status in ("Completed", "Complete"):
        jam.status = JamStatus.COMPLETED
    elif new_status == "Active":
        jam.status = JamStatus.ACTIVE
    else:
        jam.status = JamStatus.CREATED

    log_system_event("JAM_STATUS_CHANGED", {"jam_id": jam.id, "new_status": str(jam.status)})
    return _jam_to_dict(jam)
