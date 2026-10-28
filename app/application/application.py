from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.events import IndividualCreated
from app.domain.individual import Individual
from app.infrastructure.async_recorder import AsyncApplicationRecorder
from app.infrastructure.models import IndividualProjection, OutboxMessage
from app.application.unit_of_work import AsyncUnitOfWork

class AsyncApplication:

    def __init__(self, session: AsyncSession): self.session = session

    def unit_of_work(self):
        return AsyncUnitOfWork(self.session)

    async def save(self, aggregate: Individual, *, uow: AsyncUnitOfWork) -> None:
        pending = aggregate.pending_events
        if not pending: return
        result = await self.session.execute(select(IndividualProjection).where(IndividualProjection.id == aggregate.id).with_for_update())
        projection = result.scalar_one_or_none()
        stored_version = 0 if projection is None else projection.version
        base_version = aggregate.version - len(pending)
        if stored_version != base_version:
            raise HTTPException(status_code=409, detail={"message":"Versão concorrente detectada", "stored_version":stored_version, "aggregate_base_version":base_version})
        rows = await uow.recorder.append(aggregate_id=aggregate.id, expected_version=stored_version, events=pending)
        created = next((e for e in pending if isinstance(e, IndividualCreated)), None)
        if projection is None:
            if created is None: raise ValueError("O primeiro evento precisa ser IndividualCreated")
            projection = IndividualProjection(id=aggregate.id, name=aggregate.name, version=aggregate.version, created_at=created.occurred_at, updated_at=pending[-1].occurred_at)
            self.session.add(projection)
        else:
            projection.name = aggregate.name; projection.version = aggregate.version; projection.updated_at = pending[-1].occurred_at
        for row in rows:
            routing_key = {"IndividualCreated":"individual.created", "IndividualRenamed":"individual.renamed"}[row.event_type]
            self.session.add(OutboxMessage(event_id=row.event_id, aggregate_id=row.aggregate_id, event_type=row.event_type, routing_key=routing_key, payload={"event_id":str(row.event_id), "aggregate_id":str(row.aggregate_id), "aggregate_version":row.aggregate_version, "event_type":row.event_type, **row.payload}, status="PENDING", attempts=0))
        await self.session.flush(); uow.register_aggregate(aggregate)

    async def get(self, aggregate_id: UUID) -> Individual:
        rows = await AsyncApplicationRecorder(self.session).get_events(aggregate_id)
        if not rows: raise HTTPException(status_code=404, detail="Indivíduo não encontrado")
        return Individual.rehydrate([AsyncApplicationRecorder.deserialize(r.event_type, r.payload) for r in rows])

    async def get_projection(self, aggregate_id: UUID) -> IndividualProjection:
        result = await self.session.execute(select(IndividualProjection).where(IndividualProjection.id == aggregate_id))
        obj = result.scalar_one_or_none()
        if obj is None: raise HTTPException(status_code=404, detail="Indivíduo não encontrado")
        return obj
