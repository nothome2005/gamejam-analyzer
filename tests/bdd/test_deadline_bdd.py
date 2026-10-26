"""
BDD Specification by Example: Soft Deadline & Late Penalty
Scenario: BDD-SC-002
"""
from datetime import datetime, timezone
from src.submissions.service import SubmissionService
from src.submissions.models import SubmissionCreate, SubmissionStatus

def test_bdd_sc_002_soft_deadline_late_submission():
    """
    Scenario: М'який дедлайн: подання проєкту із запізненням на 45 хвилин (BDD-SC-002)
      Given джем "Winter Indie Jam 2026" має дедлайн прийому робіт 2026-10-02 20:00 UTC
      And поточний серверний час становить 2026-10-02 20:45 UTC
      And період суддівства ще не розпочався (дедлайн закриття 2026-10-02 23:00 UTC)
      When капітан команди "RetroSquad" надсилає проєкт "Neon Dash"
      Then система успішно приймає проєкт зі статусом "Submitted"
      And прапорець "is_late" встановлюється у "true"
      And система фіксує тривалість запізнення "late_minutes = 45"
      And команді нараховується штраф "late_penalty"
    """
    service = SubmissionService()
    deadline = datetime(2026, 10, 2, 20, 0, tzinfo=timezone.utc)
    submitted = datetime(2026, 10, 2, 20, 45, tzinfo=timezone.utc)
    review_deadline = datetime(2026, 10, 2, 23, 0, tzinfo=timezone.utc)

    payload = SubmissionCreate(
        jam_id="jam-winter",
        team_id="team-retro",
        title="Neon Dash",
        engine="Unity 2023",
        git_url="https://github.com/retrosquad/neon-dash.git",
        commit_hash="f5e4d3c2b1a099887766554433221100aabbccdd",
        sha256_checksum="a1b2c3d4e5f60718293a4b5c6d7e8f901234567890abcdef1234567890abcdef",
        build_url="https://retrosquad.itch.io/neon-dash",
        build_size_mb=250.0
    )

    sub = service.submit_project(
        payload=payload,
        submission_deadline=deadline,
        review_deadline=review_deadline,
        submitted_at=submitted,
        penalty_per_hour_percent=5.0
    )

    assert sub.status == SubmissionStatus.SUBMITTED
    assert sub.is_late is True
    assert sub.late_minutes == 45
    assert sub.penalty_points > 0.0
