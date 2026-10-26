import pytest
from datetime import datetime, timezone, timedelta
from src.jams.service import JamService, JamValidationError
from src.jams.models import JamCreate

def test_create_jam_valid(sample_jam_dates):
    service = JamService()
    payload = JamCreate(
        title="Winter Indie Jam 2026",
        theme="Survival and Hope",
        start_time=sample_jam_dates["start_time"],
        submission_deadline=sample_jam_dates["submission_deadline"],
        review_deadline=sample_jam_dates["review_deadline"]
    )
    jam = service.create_jam(payload)
    assert jam.id.startswith("jam-")
    assert jam.title == "Winter Indie Jam 2026"

def test_create_jam_invalid_dates_order():
    service = JamService()
    now = datetime.now(timezone.utc)
    # Deadline before start
    payload = JamCreate(
        title="Bad Dates Jam",
        theme="Error",
        start_time=now + timedelta(days=2),
        submission_deadline=now + timedelta(days=1),
        review_deadline=now + timedelta(days=3)
    )
    with pytest.raises(JamValidationError, match="start_time must be earlier than submission_deadline"):
        service.create_jam(payload)
