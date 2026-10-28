from datetime import datetime
from typing import Any
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.events import IndividualCreated, IndividualRenamed
from app.infrastructure.models import StoredEventRecord
class AsyncApplicationRecorder:
    """Recorder async próprio; não herda do recorder síncrono upstream."""
    def __init__(self, session: AsyncSession): self.session = session
    @staticmethod
    def serialize(event):
        if isinstance(event, IndividualCreated):
            return "IndividualCreated", {"individual_id": str(event.individual_id), "name": event.name, "occurred_at": event.occurred_at.isoformat()}
        if isinstance(event, IndividualRenamed):
            return "IndividualRenamed", {"individual_id": str(event.individual_id), "old_name": event.old_name, "new_name": event.new_name, "occurred_at": event.occurred_at.isoformat()}
        raise TypeError(f"Evento não suportado: {type(event)!r}")
    @staticmethod
    def deserialize(event_type: str, payload: dict[str, Any]):
        if event_type == "IndividualCreated": return IndividualCreated(UUID(payload["individual_id"]), payload["name"], datetime.fromisoformat(payload["occurred_at"]))
        if event_type == "IndividualRenamed": return IndividualRenamed(UUID(payload["individual_id"]), payload["old_name"], payload["new_name"], datetime.fromisoformat(payload["occurred_at"]))
        raise ValueError(f"Evento desconhecido: {event_type}")
    async def append(self, *, aggregate_id: UUID, expected_version: int, events):
        rows = []
        for version, event in enumerate(events, start=expected_version + 1):
            event_type, payload = self.serialize(event)
            rows.append(StoredEventRecord(aggregate_id=aggregate_id, aggregate_version=version, event_type=event_type, payload=payload, occurred_at=event.occurred_at))
        self.session.add_all(rows); await self.session.flush()
        return rows
    async def get_events(self, aggregate_id: UUID):
        result = await self.session.execute(select(StoredEventRecord).where(StoredEventRecord.aggregate_id == aggregate_id).order_by(StoredEventRecord.aggregate_version))
        return list(result.scalars().all())
