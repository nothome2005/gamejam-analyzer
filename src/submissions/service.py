import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from .models import Submission, SubmissionCreate, SubmissionStatus
from .validators import validate_sha256_hash, validate_git_url, SubmissionValidationError
from .deadline_service import DeadlineService

class SubmissionService:
    def __init__(self):
        self._submissions: Dict[str, Submission] = {}

    def submit_project(
        self,
        payload: SubmissionCreate,
        submission_deadline: datetime,
        review_deadline: datetime,
        submitted_at: Optional[datetime] = None,
        penalty_per_hour_percent: float = 5.0
    ) -> Submission:
        if submitted_at is None:
            submitted_at = datetime.now(timezone.utc)

        # 1. Validate SHA-256 (AC-F-003, BDD-SC-003)
        valid_checksum = validate_sha256_hash(payload.sha256_checksum)

        # 2. Validate Git URL
        valid_git_url = validate_git_url(payload.git_url)

        # 3. Validate Build size limit <= 500 MB (AC-F-004, BDD-SC-006)
        if payload.build_size_mb > 500.0:
            raise SubmissionValidationError(
                f"Розмір білда ({payload.build_size_mb} МБ) перевищує допустимий ліміт джему (500 МБ)"
            )

        # 4. Soft Deadline evaluation (AC-F-005, BDD-SC-002)
        deadline_result = DeadlineService.evaluate_submission_time(
            submitted_at=submitted_at,
            submission_deadline=submission_deadline,
            review_deadline=review_deadline,
            penalty_per_hour_percent=penalty_per_hour_percent
        )

        sub_id = f"sub-{uuid.uuid4().hex[:8]}"
        submission = Submission(
            id=sub_id,
            jam_id=payload.jam_id,
            team_id=payload.team_id,
            title=payload.title,
            engine=payload.engine,
            git_url=valid_git_url,
            commit_hash=payload.commit_hash,
            sha256_checksum=valid_checksum,
            build_url=payload.build_url,
            build_size_mb=payload.build_size_mb,
            asset_inventory=payload.asset_inventory,
            status=SubmissionStatus.SUBMITTED,
            submitted_at=submitted_at,
            is_late=deadline_result.is_late,
            late_minutes=deadline_result.late_minutes,
            penalty_points=deadline_result.penalty_points
        )
        self._submissions[sub_id] = submission
        return submission

    def get_submission(self, submission_id: str) -> Optional[Submission]:
        return self._submissions.get(submission_id)

    def list_submissions_by_jam(self, jam_id: str) -> List[Submission]:
        return [s for s in self._submissions.values() if s.jam_id == jam_id]
