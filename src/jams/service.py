import uuid
from typing import Dict, List, Optional
from .models import Jam, JamCreate, JamStatus

class JamValidationError(ValueError):
    """Raised when jam parameters violate AC-F-001."""
    pass

class JamService:
    def __init__(self):
        self._jams: Dict[str, Jam] = {}

    def create_jam(self, payload: JamCreate) -> Jam:
        """
        Creates a jam and validates that start_time < submission_deadline < review_deadline (AC-F-001).
        """
        if payload.start_time >= payload.submission_deadline:
            raise JamValidationError("start_time must be earlier than submission_deadline")
        if payload.submission_deadline >= payload.review_deadline:
            raise JamValidationError("submission_deadline must be earlier than review_deadline")

        jam_id = f"jam-{uuid.uuid4().hex[:8]}"
        jam = Jam(
            id=jam_id,
            title=payload.title,
            theme=payload.theme,
            start_time=payload.start_time,
            submission_deadline=payload.submission_deadline,
            review_deadline=payload.review_deadline,
            penalty_per_hour_percent=payload.penalty_per_hour_percent,
            status=JamStatus.ACTIVE
        )
        self._jams[jam_id] = jam
        return jam

    def get_jam(self, jam_id: str) -> Optional[Jam]:
        return self._jams.get(jam_id)

    def list_jams(self) -> List[Jam]:
        return list(self._jams.values())
