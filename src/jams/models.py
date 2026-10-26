from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

class JamStatus(str, Enum):
    CREATED = "Created"
    ACTIVE = "Active"
    UNDER_REVIEW = "Under Review"
    COMPLETED = "Completed"

@dataclass
class JamCreate:
    title: str
    theme: str
    start_time: datetime
    submission_deadline: datetime
    review_deadline: datetime
    penalty_per_hour_percent: float = 5.0

@dataclass
class Jam:
    id: str
    title: str
    theme: str
    start_time: datetime
    submission_deadline: datetime
    review_deadline: datetime
    status: JamStatus = JamStatus.CREATED
    penalty_per_hour_percent: float = 5.0
