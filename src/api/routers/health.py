# -*- coding: utf-8 -*-
"""
Health & Diagnostics Router (SYS-01).
"""

import time
from datetime import datetime, timezone
from fastapi import APIRouter

router = APIRouter(tags=["System"])
_START_TIME = time.time()

@router.get("/health", summary="Перевірка доступності сервера та UTC часу")
def get_health():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": round(time.time() - _START_TIME, 1)
    }
