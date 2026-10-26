from dataclasses import dataclass, field
from typing import List

@dataclass
class Participant:
    user_id: str
    username: str
    specialization: str  # e.g. "Gameplay Programmer", "2D Artist"

@dataclass
class Team:
    id: str
    name: str
    jam_id: str
    captain_id: str
    members: List[Participant] = field(default_factory=list)
