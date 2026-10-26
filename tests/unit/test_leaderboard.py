from src.submissions.models import Submission, SubmissionStatus
from src.evaluations.models import Evaluation
from src.analytics.leaderboard import calculate_leaderboard

def test_leaderboard_sorting_and_penalties():
    sub1 = Submission(
        id="sub-1", jam_id="jam-1", team_id="team-1", title="Game A", engine="Godot",
        git_url="https://github.com/a/a.git", commit_hash="c1", sha256_checksum="h1",
        build_url="http://a", build_size_mb=100, asset_inventory=[],
        status=SubmissionStatus.SUBMITTED, penalty_points=0.5
    )
    sub2 = Submission(
        id="sub-2", jam_id="jam-1", team_id="team-2", title="Game B", engine="Unity",
        git_url="https://github.com/b/b.git", commit_hash="c2", sha256_checksum="h2",
        build_url="http://b", build_size_mb=200, asset_inventory=[],
        status=SubmissionStatus.SUBMITTED, penalty_points=0.0
    )

    # Evaluations: sub1 has raw score 5.0, sub2 has raw score 4.6
    ev1 = Evaluation(id="e1", judge_id="j1", submission_id="sub-1", gameplay=5, theme_relevance=5, graphics=5, audio=5, code_quality=5)
    ev2 = Evaluation(id="e2", judge_id="j1", submission_id="sub-2", gameplay=5, theme_relevance=4, graphics=5, audio=5, code_quality=4)

    board = calculate_leaderboard([sub1, sub2], [ev1, ev2])

    assert len(board) == 2
    # sub2: 4.6 - 0.0 = 4.6
    # sub1: 5.0 - 0.5 = 4.5
    assert board[0].submission_id == "sub-2"
    assert board[0].rank == 1
    assert board[1].submission_id == "sub-1"
    assert board[1].rank == 2
