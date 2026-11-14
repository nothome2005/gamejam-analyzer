# -*- coding: utf-8 -*-
"""
Catalog Router (REQ-F-010, POS-09).
"""

from typing import Optional
from fastapi import APIRouter, Query
from src.api.state import services

router = APIRouter(prefix="/catalog", tags=["Catalog"])

@router.get("/jams", summary="Публічний каталог подій")
def get_catalog_jams():
    jams = services.jam_service.list_jams()
    return [
        {
            "id": j.id,
            "title": j.title,
            "theme": j.theme,
            "status": j.status.value if hasattr(j.status, "value") else str(j.status)
        }
        for j in jams
    ]

@router.get("/projects", summary="Публічна галерея проєктів (REQ-F-010, REQ-F-011)")
def get_catalog_projects(
    engine: Optional[str] = Query(None),
    genre: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50)
):
    catalog_res = services.catalog_service.get_public_catalog(
        engine=engine,
        genre=genre,
        page=page,
        page_size=page_size
    )
    items = catalog_res.get("items", [])
    result = []
    for sub in items:
        result.append({
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
        })
    return result
