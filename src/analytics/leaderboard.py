from dataclasses import dataclass
from typing import List, Dict
from src.submissions.models import Submission
from src.evaluations.models import Evaluation

@dataclass
class LeaderboardEntry:
    rank: int
    submission_id: str
    title: str
    team_id: str
    gameplay_score: float
    theme_score: float
    raw_score: float
    penalty_points: float
    final_score: float

def calculate_leaderboard(
    submissions: List[Submission],
    evaluations: List[Evaluation]
) -> List[LeaderboardEntry]:
    """
    Computes deterministic leaderboard with tie-breaking (AC-F-008, REQ-NF-001).
    Ranked by final_score DESC, then gameplay_score DESC, then theme_score DESC.
    """
    eval_by_sub: Dict[str, List[Evaluation]] = {}
    for ev in evaluations:
        eval_by_sub.setdefault(ev.submission_id, []).append(ev)

    entries = []
    for sub in submissions:
        sub_evals = eval_by_sub.get(sub.id, [])
        if not sub_evals:
            raw_score = 0.0
            gameplay_avg = 0.0
            theme_avg = 0.0
        else:
            gameplay_avg = sum(e.gameplay for e in sub_evals) / len(sub_evals)
            theme_avg = sum(e.theme_relevance for e in sub_evals) / len(sub_evals)
            raw_score = sum(e.average_score for e in sub_evals) / len(sub_evals)

        final_score = max(0.0, round(raw_score - sub.penalty_points, 2))

        entries.append({
            "submission_id": sub.id,
            "title": sub.title,
            "team_id": sub.team_id,
            "gameplay_score": round(gameplay_avg, 2),
            "theme_score": round(theme_avg, 2),
            "raw_score": round(raw_score, 2),
            "penalty_points": sub.penalty_points,
            "final_score": final_score
        })

    # Sort deterministically
    entries.sort(key=lambda x: (x["final_score"], x["gameplay_score"], x["theme_score"]), reverse=True)

    result = []
    for i, item in enumerate(entries, start=1):
        result.append(LeaderboardEntry(rank=i, **item))
    return result
