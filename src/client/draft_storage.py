import json
from typing import Dict, Any, Optional

class DraftStorage:
    """
    Simulates frontend client-side draft auto-save and restoration (AC-NF-004).
    """
    def __init__(self):
        self._storage: Dict[str, str] = {}

    def save_draft(self, form_key: str, data: Dict[str, Any]) -> None:
        self._storage[form_key] = json.dumps(data)

    def restore_draft(self, form_key: str) -> Optional[Dict[str, Any]]:
        raw = self._storage.get(form_key)
        return json.loads(raw) if raw else None

    def clear_draft(self, form_key: str) -> None:
        self._storage.pop(form_key, None)
