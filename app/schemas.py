from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
class CreateIndividualRequest(BaseModel): name: str = Field(min_length=1, max_length=200)
class RenameIndividualRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    expected_version: int = Field(ge=1)
class IndividualResponse(BaseModel):
    id: UUID; name: str; version: int; created_at: datetime; updated_at: datetime
class StoredEventResponse(BaseModel):
    sequence_id: int; event_id: UUID; aggregate_id: UUID; aggregate_version: int; event_type: str; payload: dict; occurred_at: datetime
