# -*- coding: utf-8 -*-
"""
Глобальний стан та DI-контейнер доменних сервісів системи Game Jam Analyzer.
Забезпечує розділення шарів (Separation of Concerns) та єдине сховище сутностей.
"""

from src.jams.service import JamService
from src.teams.service import TeamService
from src.submissions.service import SubmissionService
from src.evaluations.service import EvaluationService
from src.audit.logger import AuditLogger
from src.catalog.service import CatalogService

class ServiceContainer:
    def __init__(self):
        self.jam_service = JamService()
        self.team_service = TeamService()
        self.submission_service = SubmissionService()
        self.evaluation_service = EvaluationService()
        self.audit_logger = AuditLogger()
        self.catalog_service = CatalogService()

    def reset(self):
        """Скидання стану (для ізольованих тестових прогонів)."""
        self.jam_service = JamService()
        self.team_service = TeamService()
        self.submission_service = SubmissionService()
        self.evaluation_service = EvaluationService()
        self.audit_logger = AuditLogger()
        self.catalog_service = CatalogService()

services = ServiceContainer()
