import uuid
from typing import Dict, List
from .models import Evaluation, EvaluationCreate

class EvaluationError(ValueError):
    pass

class EvaluationService:
    def __init__(self):
        self._evaluations: Dict[str, Evaluation] = {}

    def submit_evaluation(self, payload: EvaluationCreate, judge_team_id: str = None, submission_team_id: str = None) -> Evaluation:
        """
        Records evaluation (AC-F-007, BDD-SC-005). Validates scores are in range [1, 5]
        and prevents judge from evaluating their own team.
        """
        if judge_team_id and submission_team_id and judge_team_id == submission_team_id:
            raise EvaluationError("Суддя не може оцінювати проєкт власної команди")

        for name, score in [
            ("gameplay", payload.gameplay),
            ("theme_relevance", payload.theme_relevance),
            ("graphics", payload.graphics),
            ("audio", payload.audio),
            ("code_quality", payload.code_quality)
        ]:
            if not isinstance(score, int) or score < 1 or score > 5:
                raise EvaluationError(f"Оцінка за {name} повинна бути цілим числом від 1 до 5")

        eval_id = f"eval-{uuid.uuid4().hex[:8]}"
        ev = Evaluation(
            id=eval_id,
            judge_id=payload.judge_id,
            submission_id=payload.submission_id,
            gameplay=payload.gameplay,
            theme_relevance=payload.theme_relevance,
            graphics=payload.graphics,
            audio=payload.audio,
            code_quality=payload.code_quality,
            comment=payload.comment
        )
        self._evaluations[eval_id] = ev
        return ev

    def get_evaluations_for_submission(self, submission_id: str) -> List[Evaluation]:
        return [e for e in self._evaluations.values() if e.submission_id == submission_id]
