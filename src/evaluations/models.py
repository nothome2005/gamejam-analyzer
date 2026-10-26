from dataclasses import dataclass
from typing import Optional

@dataclass
class EvaluationCreate:
    judge_id: str
    submission_id: str
    gameplay: int
    theme_relevance: int
    graphics: int
    audio: int
    code_quality: int
    comment: Optional[str] = None

@dataclass
class Evaluation:
    id: str
    judge_id: str
    submission_id: str
    gameplay: int
    theme_relevance: int
    graphics: int
    audio: int
    code_quality: int
    comment: Optional[str] = None

    @property
    def average_score(self) -> float:
        return (self.gameplay + self.theme_relevance + self.graphics + self.audio + self.code_quality) / 5.0
