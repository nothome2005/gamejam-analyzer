"""
BDD Specification by Example: Submission & Audit Verification
Scenario: BDD-SC-001 & BDD-SC-003
"""
import pytest
from datetime import datetime, timezone, timedelta
from src.submissions.service import SubmissionService
from src.submissions.models import SubmissionCreate, SubmissionStatus
from src.submissions.validators import SubmissionValidationError

def test_bdd_sc_001_on_time_submission_with_audit_data():
    """
    Scenario: Вчасне подання гри з коректними контрольними даними (BDD-SC-001)
      Given джем "Winter Indie Jam 2026" перебуває у статусі "Active"
      And поточний час 18:00 UTC менший за дедлайн 20:00 UTC
      When капітан надсилає проєкт
      Then система зберігає сабмішн зі статусом "Submitted"
      And прапорець "is_late" встановлюється у "false"
      And штрафні бали дорівнюють 0
    """
    service = SubmissionService()
    now = datetime(2026, 10, 2, 18, 0, tzinfo=timezone.utc)
    deadline = datetime(2026, 10, 2, 20, 0, tzinfo=timezone.utc)
    review_deadline = datetime(2026, 10, 2, 23, 0, tzinfo=timezone.utc)

    payload = SubmissionCreate(
        jam_id="jam-winter",
        team_id="team-pixel",
        title="Frostbite Odyssey",
        engine="Godot 4.3",
        git_url="https://github.com/pixelcrafters/frostbite-game.git",
        commit_hash="e4d909c290d0fb1ca068ffaddf22cbd0a6042db5",
        sha256_checksum="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        build_url="https://pixelcrafters.itch.io/frostbite-odyssey",
        build_size_mb=120.0,
        asset_inventory=["Kenney UI Audio Pack", "CC-BY 4.0 Textures"]
    )

    sub = service.submit_project(
        payload=payload,
        submission_deadline=deadline,
        review_deadline=review_deadline,
        submitted_at=now
    )

    assert sub.status == SubmissionStatus.SUBMITTED
    assert sub.is_late is False
    assert sub.late_minutes == 0
    assert sub.penalty_points == 0.0

def test_bdd_sc_003_rejection_of_invalid_sha256_checksum():
    """
    Scenario: Відхилення некоректного формату контрольної суми SHA-256 (BDD-SC-003)
      Given капітан команди заповнює форму реєстрації проєкту
      When у полі "sha256_checksum" введено значення "invalid-hash-string-too-short"
      Then система відхиляє збереження з вимогою 64 шістнадцяткових символів
    """
    service = SubmissionService()
    now = datetime(2026, 10, 2, 18, 0, tzinfo=timezone.utc)
    deadline = datetime(2026, 10, 2, 20, 0, tzinfo=timezone.utc)
    review_deadline = datetime(2026, 10, 2, 23, 0, tzinfo=timezone.utc)

    payload = SubmissionCreate(
        jam_id="jam-winter",
        team_id="team-pixel",
        title="Invalid Hash Game",
        engine="Godot",
        git_url="https://github.com/pixelcrafters/game.git",
        commit_hash="c1",
        sha256_checksum="invalid-hash-string-too-short",
        build_url="https://itch.io/game",
        build_size_mb=100.0
    )

    with pytest.raises(SubmissionValidationError, match="Контрольна сума повинна містити рівно 64 шістнадцяткові символи"):
        service.submit_project(
            payload=payload,
            submission_deadline=deadline,
            review_deadline=review_deadline,
            submitted_at=now
        )
