# -*- coding: utf-8 -*-
"""
Catalog Router (REQ-F-010, POS-09).
"""

from typing import Optional
from fastapi import APIRouter, Query
from src.api.state import services
from src.api.serializers import serialize_catalog_project

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
    return [serialize_catalog_project(sub) for sub in items]
