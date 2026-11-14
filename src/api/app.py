# -*- coding: utf-8 -*-
"""
Головний серверний додаток REST API інформаційної системи «Game Jam Analyzer».
Реалізовано на FastAPI за стандартами OpenAPI 3.0.3 та RFC 7807 (Problem Details).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from src.api.middleware import StructuredLoggingMiddleware
from src.api.errors import (
    ProblemDetailsException,
    problem_exception_handler,
    validation_exception_handler,
    domain_validation_handler,
    team_conflict_handler,
    access_denied_handler
)
from src.jams.service import JamValidationError
from src.teams.service import TeamValidationError
from src.submissions.validators import SubmissionValidationError
from src.evaluations.service import EvaluationError
from src.auth.rbac import AccessDeniedError

from src.api.routers import (
    health,
    jams,
    teams,
    submissions,
    evaluations,
    leaderboard,
    analytics,
    catalog
)

app = FastAPI(
    title="Game Jam Analyzer REST API",
    description="Офіційне серверне REST API інформаційної системи обліку та аналізу ігрових джемів.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 1. Підключення CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Наскрізне структуроване логування (LOGS)
app.add_middleware(StructuredLoggingMiddleware)

# 3. Реєстрація обробників помилок (RFC 7807 Problem Details)
app.add_exception_handler(ProblemDetailsException, problem_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(TeamValidationError, team_conflict_handler)
app.add_exception_handler(SubmissionValidationError, domain_validation_handler)
app.add_exception_handler(JamValidationError, domain_validation_handler)
app.add_exception_handler(EvaluationError, domain_validation_handler)
app.add_exception_handler(AccessDeniedError, access_denied_handler)

# 4. Підключення роутерів
app.include_router(health.router)
app.include_router(jams.router)
app.include_router(teams.router)
app.include_router(submissions.router)
app.include_router(evaluations.router)
app.include_router(leaderboard.router)
app.include_router(analytics.router)
app.include_router(catalog.router)
