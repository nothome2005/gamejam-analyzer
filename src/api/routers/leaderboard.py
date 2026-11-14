# -*- coding: utf-8 -*-
"""
Leaderboard Router (REQ-F-008, REQ-NF-001, POS-07).
"""

from fastapi import APIRouter
from src.api.state import services
from src.api.errors import ProblemDetailsException
from src.analytics.leaderboard import calculate_leaderboard

router = APIRouter(tags=["Leaderboard"])

@router.get("/jams/{jam_id}/leaderboard", summary="Отримання підсумкового лідерборду джему (REQ-F-008)")
def get_jam_leaderboard(jam_id: str):
    jam = services.jam_service.get_jam(jam_id)
    if not jam:
        raise ProblemDetailsException(status=404, title="Not Found", detail=f"Джем '{jam_id}' не знайдено.")

    subs = services.submission_service.list_submissions_by_jam(jam_id)
    all_evals = []
    for s in subs:
        all_evals.extend(services.evaluation_service.get_evaluations_for_submission(s.id))

    entries = calculate_leaderboard(subs, all_evals)
    result = []
    for e in entries:
        result.append({
            "rank": e.rank,
            "submission_id": e.submission_id,
            "project_name": e.title,
            "title": e.title,
            "team_id": e.team_id,
            "gameplay_score": e.gameplay_score,
            "theme_score": e.theme_score,
            "raw_score": e.raw_score,
            "penalty_points": e.penalty_points,
            "final_score": e.final_score
        })
    return result
