from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Any

@dataclass(frozen=True)
class AuditEntry:
    id: int
    timestamp: datetime
    entity_type: str
    entity_id: str
    field_name: str
    old_value: Any
    new_value: Any
    author_id: str

class AuditLogger:
    """
    Immutable audit log for changes to submissions and checksums (AC-NF-003).
    """
    def __init__(self):
        self._log: List[AuditEntry] = []
        self._next_id = 1

    def record_change(self, entity_type: str, entity_id: str, field_name: str, old_value: Any, new_value: Any, author_id: str) -> AuditEntry:
        entry = AuditEntry(
            id=self._next_id,
            timestamp=datetime.now(timezone.utc),
            entity_type=entity_type,
            entity_id=entity_id,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            author_id=author_id
        )
        self._log.append(entry)
        self._next_id += 1
        return entry

    def get_history(self, entity_id: str) -> List[AuditEntry]:
        return [e for e in self._log if e.entity_id == entity_id]
