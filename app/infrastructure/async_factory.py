"""Factory simples para criar datastore e recorder assíncronos.

Esta fábrica pertence ao adaptador deste projeto; não implementa a Factory síncrona
interna de eventsourcing_sqlalchemy==1.0.1.
"""
from app.infrastructure.async_datastore import AsyncSQLAlchemyDatastore
from app.infrastructure.async_recorder import AsyncApplicationRecorder


class AsyncSQLAlchemyFactory:
    def __init__(self, url: str, *, echo: bool = False, pool_size: int = 5):
        self.datastore = AsyncSQLAlchemyDatastore(url, echo=echo, pool_size=pool_size)

    def recorder(self, session):
        return AsyncApplicationRecorder(session)

    async def close(self) -> None:
        await self.datastore.dispose()
