from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
@dataclass(frozen=True, slots=True)
class IndividualCreated:
    individual_id: UUID
    name: str
    occurred_at: datetime
@dataclass(frozen=True, slots=True)
class IndividualRenamed:
    individual_id: UUID
    old_name: str
    new_name: str
    occurred_at: datetime
