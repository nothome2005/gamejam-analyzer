# -*- coding: utf-8 -*-
"""
Analytics Router (REQ-F-009, POS-08).
"""

from fastapi import APIRouter
from src.api.state import services
from src.api.errors import ProblemDetailsException
from src.analytics.engines import aggregate_engine_stats
from src.analytics.genres import aggregate_genre_stats

router = APIRouter(tags=["Analytics"])

@router.get("/analytics/genres", summary="Глобальна статистика використання ігрових жанрів (REQ-F-011)")
def get_global_genre_analytics():
    all_subs = list(services.submission_service._submissions.values())
    stats = aggregate_genre_stats(all_subs)
    return [
        {
            "genre": s.genre,
            "count": s.count,
            "percentage": s.percentage
        }
        for s in stats
    ]

@router.get("/analytics/engines", summary="Глобальна статистика використання ігрових рушіїв (REQ-F-009)")
def get_global_engine_analytics():
    all_subs = list(services.submission_service._submissions.values())
    stats = aggregate_engine_stats(all_subs)
    return [
        {
            "engine": s.engine,
            "count": s.count,
            "percentage": s.percentage
        }
        for s in stats
    ]

@router.get("/jams/{jam_id}/analytics/engines", summary="Статистика ігрових рушіїв конкретного джему")
def get_jam_engine_analytics(jam_id: str):
    jam = services.jam_service.get_jam(jam_id)
    if not jam:
        raise ProblemDetailsException(status=404, title="Not Found", detail=f"Джем '{jam_id}' не знайдено.")

    jam_subs = services.submission_service.list_submissions_by_jam(jam_id)
    stats = aggregate_engine_stats(jam_subs)
    return [
        {
            "engine": s.engine,
            "count": s.count,
            "percentage": s.percentage
        }
        for s in stats
    ]
