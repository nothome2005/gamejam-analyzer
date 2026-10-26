from datetime import datetime, timezone, timedelta
from src.submissions.deadline_service import DeadlineService

def test_on_time_submission():
    now = datetime.now(timezone.utc)
    deadline = now + timedelta(hours=2)
    review_deadline = now + timedelta(days=2)

    result = DeadlineService.evaluate_submission_time(
        submitted_at=now,
        submission_deadline=deadline,
        review_deadline=review_deadline
    )
    assert not result.is_late
    assert result.late_minutes == 0
    assert result.penalty_points == 0.0

def test_soft_deadline_45_minutes_late():
    base = datetime(2026, 10, 2, 20, 0, tzinfo=timezone.utc)
    submitted = datetime(2026, 10, 2, 20, 45, tzinfo=timezone.utc)
    review = datetime(2026, 10, 2, 23, 0, tzinfo=timezone.utc)

    result = DeadlineService.evaluate_submission_time(
        submitted_at=submitted,
        submission_deadline=base,
        review_deadline=review,
        penalty_per_hour_percent=5.0
    )
    assert result.is_late
    assert result.late_minutes == 45
    # 45 min = 1 ceil hour -> 1 * 0.05 * 5.0 = 0.25 points
    assert result.penalty_points == 0.25
