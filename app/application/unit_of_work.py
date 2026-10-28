from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.async_recorder import AsyncApplicationRecorder

class AsyncUnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session; self.recorder = AsyncApplicationRecorder(session); self._committed = False; self._aggregates = []
    def register_aggregate(self, aggregate): self._aggregates.append(aggregate)
    async def __aenter__(self): return self
    async def __aexit__(self, exc_type, exc, tb):
        if exc_type is not None or not self._committed: await self.session.rollback()
        else:
            for aggregate in self._aggregates: aggregate.mark_events_committed()
    async def commit(self):
        try: await self.session.commit()
        except Exception:
            await self.session.rollback(); raise
        self._committed = True
    async def rollback(self):
        await self.session.rollback(); self._committed = False
