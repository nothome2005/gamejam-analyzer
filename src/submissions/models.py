from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional

class SubmissionStatus(str, Enum):
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    UNDER_REVIEW = "Under Review"
    COMPLETED = "Completed"

@dataclass
class SubmissionCreate:
    jam_id: str
    team_id: str
    title: str
    engine: str
    git_url: str
    commit_hash: str
    sha256_checksum: str
    build_url: str
    build_size_mb: float
    asset_inventory: List[str] = field(default_factory=list)

@dataclass
class Submission:
    id: str
    jam_id: str
    team_id: str
    title: str
    engine: str
    git_url: str
    commit_hash: str
    sha256_checksum: str
    build_url: str
    build_size_mb: float
    asset_inventory: List[str]
    status: SubmissionStatus = SubmissionStatus.SUBMITTED
    submitted_at: Optional[datetime] = None
    is_late: bool = False
    late_minutes: int = 0
    penalty_points: float = 0.0
