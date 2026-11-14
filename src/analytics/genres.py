# -*- coding: utf-8 -*-
"""
Genre Analytics Module (REQ-F-011, AC-F-011.5, Addendum 02).
"""

from dataclasses import dataclass
from typing import List, Dict
from src.submissions.models import Submission

@dataclass
class GenreStat:
    genre: str
    count: int
    percentage: float

def aggregate_genre_stats(submissions: List[Submission]) -> List[GenreStat]:
    """
    Computes distribution and percentage of genres across submitted projects.
    """
    if not submissions:
        return []

    counts: Dict[str, int] = {}
    for sub in submissions:
        sub_genres = getattr(sub, "genres", []) or []
        for g in sub_genres:
            g_clean = g.strip()
            counts[g_clean] = counts.get(g_clean, 0) + 1

    total_submissions = len(submissions)
    stats = []
    for genre, count in counts.items():
        pct = round((count / total_submissions) * 100.0, 2)
        stats.append(GenreStat(genre=genre, count=count, percentage=pct))

    stats.sort(key=lambda s: s.count, reverse=True)
    return stats
