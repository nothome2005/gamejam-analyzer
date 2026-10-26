from enum import Enum

class Role(str, Enum):
    GUEST = "Guest"
    PARTICIPANT = "Participant"
    JUDGE = "Judge"
    ORGANIZER = "Organizer"

class AccessDeniedError(PermissionError):
    """Corresponds to HTTP 403 Forbidden (BDD-SC-004, AC-F-006)."""
    pass

def check_submission_access(user_role: Role, submission_status: str, is_own_team: bool = False) -> bool:
    """
    Guards confidential data during 'Under Review' stage (AC-F-006, REQ-NF-002, BDD-SC-004).
    """
    if submission_status == "Under Review":
        if user_role not in (Role.JUDGE, Role.ORGANIZER) and not is_own_team:
            raise AccessDeniedError("HTTP 403 Forbidden: Доступ до коду та оцінок закрито на час суддівства")
    return True
