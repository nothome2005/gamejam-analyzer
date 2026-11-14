# -*- coding: utf-8 -*-
"""
Централізована обробка винятків за стандартом RFC 7807 (Problem Details for HTTP APIs).
Формує структуровані JSON-відповіді з медіа-типом application/problem+json та логує інциденти.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from src.jams.service import JamValidationError
from src.teams.service import TeamValidationError
from src.submissions.validators import SubmissionValidationError
from src.evaluations.service import EvaluationError
from src.auth.rbac import AccessDeniedError
from src.api.middleware import log_system_event

class ProblemDetailsException(Exception):
    def __init__(
        self,
        status: int,
        title: str,
        detail: str,
        type_uri: str = None,
        instance: str = None,
        invalid_params: list = None
    ):
        self.status = status
        self.title = title
        self.detail = detail
        self.type_uri = type_uri or f"https://gamejam-analyzer.local/errors/{title.lower().replace(' ', '-')}"
        self.instance = instance
        self.invalid_params = invalid_params or []

def create_problem_response(
    status: int,
    title: str,
    detail: str,
    instance: str = "",
    type_uri: str = None,
    invalid_params: list = None
) -> JSONResponse:
    type_uri = type_uri or f"https://gamejam-analyzer.local/errors/{title.lower().replace(' ', '-')}"
    payload = {
        "type": type_uri,
        "title": title,
        "status": status,
        "detail": detail,
        "instance": instance
    }
    if invalid_params:
        payload["invalid_params"] = invalid_params

    # Фіксація інциденту в системному журналі аудиту
    log_system_event("API_PROBLEM_DETAILS_RETURNED", {
        "status": status,
        "title": title,
        "detail": detail,
        "instance": instance,
        "invalid_params_count": len(invalid_params) if invalid_params else 0
    })

    return JSONResponse(
        status_code=status,
        content=payload,
        media_type="application/problem+json"
    )

async def problem_exception_handler(request: Request, exc: ProblemDetailsException):
    return create_problem_response(
        status=exc.status,
        title=exc.title,
        detail=exc.detail,
        instance=exc.instance or request.url.path,
        type_uri=exc.type_uri,
        invalid_params=exc.invalid_params
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    invalid_params = []
    for err in exc.errors():
        field_name = ".".join(str(loc) for loc in err.get("loc", []) if loc != "body")
        invalid_params.append({
            "name": field_name,
            "reason": err.get("msg", "Помилка валідації")
        })

    return create_problem_response(
        status=422,
        title="Unprocessable Entity",
        detail="Передані дані не відповідають вимогам схеми запиту.",
        instance=request.url.path,
        invalid_params=invalid_params
    )

async def domain_validation_handler(request: Request, exc: ValueError):
    return create_problem_response(
        status=422,
        title="Unprocessable Entity",
        detail=str(exc),
        instance=request.url.path,
        invalid_params=[{"name": "payload", "reason": str(exc)}]
    )

async def team_conflict_handler(request: Request, exc: TeamValidationError):
    return create_problem_response(
        status=409,
        title="Conflict",
        detail=str(exc),
        instance=request.url.path
    )

async def access_denied_handler(request: Request, exc: AccessDeniedError):
    return create_problem_response(
        status=403,
        title="Forbidden",
        detail=str(exc),
        instance=request.url.path
    )
