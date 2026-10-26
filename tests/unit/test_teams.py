import pytest
from src.teams.service import TeamService, TeamValidationError
from src.teams.models import Participant

def test_register_team_success():
    service = TeamService()
    captain = Participant(user_id="user-1", username="Alex", specialization="Lead Programmer")
    team = service.register_team(jam_id="jam-1", name="PixelCrafters", captain=captain)

    assert team.id.startswith("team-")
    assert team.name == "PixelCrafters"
    assert len(team.members) == 1

def test_user_cannot_join_two_teams_in_same_jam():
    service = TeamService()
    user = Participant(user_id="user-1", username="Alex", specialization="Artist")
    service.register_team(jam_id="jam-1", name="Team A", captain=user)

    # Attempt to create another team in same jam with same user
    with pytest.raises(TeamValidationError, match="already belongs to a team"):
        service.register_team(jam_id="jam-1", name="Team B", captain=user)
