# -*- coding: utf-8 -*-
"""
Evaluations & Jury Scoring Router (REQ-F-006, REQ-F-007, REQ-NF-002, POS-06, NEG-03, NEG-04).
"""

from typing import List, Optional
from fastapi import APIRouter, Header, status
from pydantic import BaseModel, Field

from src.api.state import services
from src.api.errors import ProblemDetailsException
from src.api.middleware import log_system_event
from src.evaluations.models import EvaluationCreate, Evaluation
from src.jams.models import JamStatus

router = APIRouter(tags=["Evaluations"])

class EvaluationCreateDTO(BaseModel):
    judge_id: str
    gameplay_score: Optional[int] = None
    theme_score: Optional[int] = None
    originality_score: Optional[int] = None
    visual_score: Optional[int] = None
    audio_score: Optional[int] = None
    # Сумісність із доменною моделлю
    gameplay: Optional[int] = None
    theme_relevance: Optional[int] = None
    graphics: Optional[int] = None
    code_quality: Optional[int] = 4
    feedback_comment: Optional[str] = None
    comment: Optional[str] = None

def _eval_to_dict(ev: Evaluation) -> dict:
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

@router.post("/submissions/{submission_id}/evaluations", status_code=status.HTTP_201_CREATED, summary="Оцінювання проєкту суддею (REQ-F-007)")
def submit_evaluation(submission_id: str, payload: EvaluationCreateDTO):
    sub = services.submission_service.get_submission(submission_id)
    if not sub:
        raise ProblemDetailsException(status=404, title="Not Found", detail=f"Сабмішн '{submission_id}' не знайдено.")

    gp = payload.gameplay_score if payload.gameplay_score is not None else payload.gameplay
    th = payload.theme_score if payload.theme_score is not None else payload.theme_relevance
    orig = payload.originality_score if payload.originality_score is not None else 4
    vis = payload.visual_score if payload.visual_score is not None else (payload.graphics if payload.graphics is not None else 4)
    aud = payload.audio_score if payload.audio_score is not None else (payload.audio if payload.audio is not None else 4)
    code = payload.code_quality if payload.code_quality is not None else 4
    cmt = payload.feedback_comment or payload.comment or ""

    # Валідація шкали 1-5 (NEG-03)
    for name, val in [("gameplay_score", gp), ("theme_score", th), ("originality_score", orig), ("visual_score", vis), ("audio_score", aud)]:
        if val is None or not (1 <= val <= 5):
            raise ProblemDetailsException(
                status=422,
                title="Unprocessable Entity",
                detail=f"Бал за критерієм '{name}' повинен бути в діапазоні від 1 до 5 (отримано {val}).",
                invalid_params=[{"name": name, "reason": f"{name} must be between 1 and 5"}]
            )

    domain_eval = EvaluationCreate(
        judge_id=payload.judge_id,
        submission_id=submission_id,
        gameplay=gp,
        theme_relevance=th,
        graphics=vis,
        audio=aud,
        code_quality=code,
        comment=cmt
    )

    ev = services.evaluation_service.submit_evaluation(domain_eval)
    log_system_event("EVALUATION_SUBMITTED", {
        "evaluation_id": ev.id,
        "submission_id": submission_id,
        "judge_id": ev.judge_id,
        "average_score": ev.average_score
    })
    return _eval_to_dict(ev)

@router.get("/submissions/{submission_id}/evaluations", summary="Список оцінок роботи (ізольовано в Under Review)")
def get_evaluations(submission_id: str, x_user_role: Optional[str] = Header("Guest", alias="X-User-Role")):
    sub = services.submission_service.get_submission(submission_id)
    if not sub:
        raise ProblemDetailsException(status=404, title="Not Found", detail=f"Сабмішн '{submission_id}' не знайдено.")

    jam = services.jam_service.get_jam(sub.jam_id)
    # Ізоляція оцінок під час Under Review (REQ-F-006, REQ-NF-002, NEG-04)
    if jam and jam.status == JamStatus.UNDER_REVIEW:
        if x_user_role not in ("Judge", "Organizer", "Admin"):
            raise ProblemDetailsException(
                status=403,
                title="Forbidden",
                detail="Доступ до суддівських оцінок заблоковано на час активної експертизи (Under Review)."
            )

    evals = services.evaluation_service.get_evaluations_for_submission(submission_id)
    return [_eval_to_dict(e) for e in evals]
