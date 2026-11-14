# -*- coding: utf-8 -*-
"""
Teams Management Router (REQ-F-002, AC-F-002, POS-03, NEG-06).
"""

from typing import Optional
from fastapi import APIRouter, Response, status
from pydantic import BaseModel, Field

from src.api.state import services
from src.api.errors import ProblemDetailsException
from src.api.middleware import log_system_event
from src.api.serializers import serialize_team
from src.teams.models import Participant

router = APIRouter(tags=["Teams"])

# Зберігання інвайт-кодів команд: team_id -> invite_code
_TEAM_INVITES = {}

class ParticipantDTO(BaseModel):
    user_id: str
    name: Optional[str] = None
    username: Optional[str] = None
    specialization: str

class TeamCreateDTO(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    captain: ParticipantDTO

class AddMemberDTO(BaseModel):
    invite_code: Optional[str] = None
    member: ParticipantDTO

@router.post("/jams/{jam_id}/teams", status_code=status.HTTP_201_CREATED, summary="Реєстрація команди (REQ-F-002)")
def create_team(jam_id: str, payload: TeamCreateDTO):
    jam = services.jam_service.get_jam(jam_id)
    if not jam:
        raise ProblemDetailsException(status=404, title="Not Found", detail=f"Джем '{jam_id}' не знайдено.")

    captain_name = payload.captain.name or payload.captain.username or payload.captain.user_id
    captain = Participant(
        user_id=payload.captain.user_id,
        username=captain_name,
        specialization=payload.captain.specialization
    )
    captain.name = captain_name

    membership_key = (jam_id, captain.user_id)
    if membership_key in services.team_service._user_jam_membership:
        raise ProblemDetailsException(
            status=409,
            title="Conflict",
            detail=f"Користувач '{captain.user_id}' вже бере участь у іншій команді цього джему."
        )

    team = services.team_service.register_team(jam_id=jam_id, name=payload.name, captain=captain)
    invite_code = f"INV-{team.id.replace('team-', '')[:6].upper()}"
    _TEAM_INVITES[team.id] = invite_code

    log_system_event("TEAM_REGISTERED", {"team_id": team.id, "jam_id": jam_id, "captain_id": captain.user_id})
    return serialize_team(team, invite_code)

@router.get("/jams/{jam_id}/teams", summary="Список команд джему")
def get_jam_teams(jam_id: str):
    teams = [t for t in services.team_service._teams.values() if t.jam_id == jam_id]
    return [serialize_team(t, _TEAM_INVITES.get(t.id)) for t in teams]

@router.get("/teams/{team_id}", summary="Отримання даних команди")
def get_team(team_id: str):
    team = services.team_service._teams.get(team_id)
    if not team:
        raise ProblemDetailsException(status=404, title="Not Found", detail=f"Команду '{team_id}' не знайдено.")
    return serialize_team(team, _TEAM_INVITES.get(team.id))

@router.post("/teams/{team_id}/members", summary="Приєднання учасника до команди за інвайт-кодом")
def join_team(team_id: str, payload: AddMemberDTO):
    team = services.team_service._teams.get(team_id)
    if not team:
        raise ProblemDetailsException(status=404, title="Not Found", detail=f"Команду '{team_id}' не знайдено.")

    expected_invite = _TEAM_INVITES.get(team_id, f"INV-{team_id.replace('team-', '')[:6].upper()}")
    if payload.invite_code and payload.invite_code != expected_invite:
        raise ProblemDetailsException(status=400, title="Bad Request", detail="Недійсний інвайт-код команди.")

    member_name = payload.member.name or payload.member.username or payload.member.user_id
    participant = Participant(
        user_id=payload.member.user_id,
        username=member_name,
        specialization=payload.member.specialization
    )
    participant.name = member_name

    membership_key = (team.jam_id, participant.user_id)
    if membership_key in services.team_service._user_jam_membership:
        raise ProblemDetailsException(
            status=409,
            title="Conflict",
            detail=f"Користувач '{participant.user_id}' вже перебуває у команді цього джему."
        )

    services.team_service.add_member(team_id, participant)
    log_system_event("TEAM_MEMBER_JOINED", {"team_id": team.id, "user_id": participant.user_id})
    return serialize_team(team, expected_invite)

@router.delete("/teams/{team_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Виключення учасника з команди")
def remove_team_member(team_id: str, user_id: str):
    team = services.team_service._teams.get(team_id)
    if not team:
        raise ProblemDetailsException(status=404, title="Not Found", detail=f"Команду '{team_id}' не знайдено.")

    original_len = len(team.members)
    team.members = [m for m in team.members if m.user_id != user_id]
    if len(team.members) == original_len:
        raise ProblemDetailsException(status=404, title="Not Found", detail="Учасника не знайдено у складі команди.")

    services.team_service._user_jam_membership.pop((team.jam_id, user_id), None)
    log_system_event("TEAM_MEMBER_REMOVED", {"team_id": team.id, "user_id": user_id})
    return Response(status_code=status.HTTP_204_NO_CONTENT)
