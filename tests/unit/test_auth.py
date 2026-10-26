import pytest
from src.auth.rbac import Role, AccessDeniedError, check_submission_access

def test_guest_access_denied_under_review():
    with pytest.raises(AccessDeniedError, match="HTTP 403 Forbidden"):
        check_submission_access(user_role=Role.GUEST, submission_status="Under Review", is_own_team=False)

def test_judge_access_allowed_under_review():
    assert check_submission_access(user_role=Role.JUDGE, submission_status="Under Review") is True

def test_organizer_access_allowed_under_review():
    assert check_submission_access(user_role=Role.ORGANIZER, submission_status="Under Review") is True

def test_own_team_access_allowed_under_review():
    assert check_submission_access(user_role=Role.PARTICIPANT, submission_status="Under Review", is_own_team=True) is True
