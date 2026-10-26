from typing import List, Optional
from src.submissions.models import Submission

class CatalogService:
    def __init__(self, submissions: Optional[List[Submission]] = None):
        self._submissions = submissions or []

    def get_public_catalog(
        self,
        engine: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> dict:
        """
        Public catalog with pagination and engine filtering (AC-F-010).
        """
        items = self._submissions
        if engine:
            items = [s for s in items if s.engine.lower() == engine.lower()]

        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_items = items[start_idx:end_idx]

        return {
            "total": len(items),
            "page": page,
            "page_size": page_size,
            "items": paginated_items
        }
