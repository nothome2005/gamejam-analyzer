import math
from dataclasses import dataclass
from datetime import datetime

class DeadlineExceededError(ValueError):
    """Raised when submission is attempted after review period closed."""
    pass

@dataclass
class DeadlineResult:
    is_late: bool
    late_minutes: int
    penalty_points: float

class DeadlineService:
    @staticmethod
    def evaluate_submission_time(
        submitted_at: datetime,
        submission_deadline: datetime,
        review_deadline: datetime,
        penalty_per_hour_percent: float = 5.0
    ) -> DeadlineResult:
        """
        Evaluates submission timestamp against soft deadline policy (AC-F-005, BDD-SC-002).
        """
        if submitted_at > review_deadline:
            raise DeadlineExceededError("Прийом робіт остаточно завершено. Період суддівства закрито.")

        if submitted_at <= submission_deadline:
            return DeadlineResult(is_late=False, late_minutes=0, penalty_points=0.0)

        # Soft deadline triggered
        delta = submitted_at - submission_deadline
        late_minutes = int(delta.total_seconds() // 60)
        late_hours = math.ceil(late_minutes / 60.0)

        # Penalty: penalty_per_hour_percent * late_hours (scaled to points or percent)
        penalty_points = round(late_hours * (penalty_per_hour_percent / 100.0) * 5.0, 2)

        return DeadlineResult(
            is_late=True,
            late_minutes=late_minutes,
            penalty_points=penalty_points
        )
