import uuid
from typing import Dict, List, Optional
from .models import Team, Participant

class TeamValidationError(ValueError):
    pass

class TeamService:
    def __init__(self):
        self._teams: Dict[str, Team] = {}
        # (jam_id, user_id) -> team_id to enforce single team per jam (AC-F-002)
        self._user_jam_membership: Dict[tuple, str] = {}

    def register_team(self, jam_id: str, name: str, captain: Participant) -> Team:
        membership_key = (jam_id, captain.user_id)
        if membership_key in self._user_jam_membership:
            raise TeamValidationError(f"User {captain.user_id} already belongs to a team in jam {jam_id}")

        team_id = f"team-{uuid.uuid4().hex[:8]}"
        team = Team(
            id=team_id,
            name=name,
            jam_id=jam_id,
            captain_id=captain.user_id,
            members=[captain]
        )
        self._teams[team_id] = team
        self._user_jam_membership[membership_key] = team_id
        return team

    def add_member(self, team_id: str, participant: Participant) -> Team:
        team = self._teams.get(team_id)
        if not team:
            raise TeamValidationError("Team not found")

        membership_key = (team.jam_id, participant.user_id)
        if membership_key in self._user_jam_membership:
            raise TeamValidationError(f"User {participant.user_id} already belongs to a team in this jam")

        team.members.append(participant)
        self._user_jam_membership[membership_key] = team_id
        return team
