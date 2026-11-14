# -*- coding: utf-8 -*-
"""
Наскрізне структуроване логування (LOGS) для всіх операцій REST API.
Фіксує кожен запит, час відповіді (latency), статус-код, X-Request-ID та деталі дій
у файлі logs/system_execution.log згідно зі стандартом SDD та вимогами лабораторної роботи.
"""

import os
import json
import time
import uuid
from datetime import datetime, timezone
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

LOGS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "logs"))
os.makedirs(LOGS_DIR, exist_ok=True)
EXECUTION_LOG_PATH = os.path.join(LOGS_DIR, "system_execution.log")

def log_system_event(event_type: str, details: dict):
    """
    Запис довільної системної або доменної події у журнал logs/system_execution.log.
    """
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "details": details
    }
    with open(EXECUTION_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("X-Request-ID", f"req-{uuid.uuid4().hex[:12]}")
        start_time = time.time()

        response = await call_next(request)
        latency_ms = round((time.time() - start_time) * 1000, 2)

        client_ip = request.client.host if request.client else "unknown"
        user_role = request.headers.get("X-User-Role", "Guest")

        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": req_id,
            "method": request.method,
            "path": request.url.path,
            "query": str(request.url.query),
            "status_code": response.status_code,
            "latency_ms": latency_ms,
            "client_ip": client_ip,
            "user_role": user_role
        }

        with open(EXECUTION_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_record, ensure_ascii=False) + "\n")

        response.headers["X-Request-ID"] = req_id
        response.headers["X-Response-Time-Ms"] = str(latency_ms)
        return response
