from dataclasses import dataclass
from typing import List, Dict
from src.submissions.models import Submission

@dataclass
class EngineStat:
    engine: str
    count: int
    percentage: float

def aggregate_engine_stats(submissions: List[Submission]) -> List[EngineStat]:
    """
    Computes distribution of game engines used in submissions (AC-F-009).
    """
    if not submissions:
        return []

    counts: Dict[str, int] = {}
    for sub in submissions:
        engine_name = sub.engine.strip() if sub.engine else "Unknown"
        counts[engine_name] = counts.get(engine_name, 0) + 1

    total = len(submissions)
    stats = []
    for eng, count in counts.items():
        pct = round((count / total) * 100.0, 2)
        stats.append(EngineStat(engine=eng, count=count, percentage=pct))

    stats.sort(key=lambda s: s.count, reverse=True)
    return stats
