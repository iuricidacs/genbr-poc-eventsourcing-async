from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
class AsyncSQLAlchemyDatastore:
    """Gerencia engine e sessões async; não bloqueia o event loop."""
    def __init__(self, url: str, *, echo: bool = False, pool_size: int = 5):
        if not url.startswith("postgresql+asyncpg://"):
            raise ValueError("Use uma URL postgresql+asyncpg://")
        self.engine: AsyncEngine = create_async_engine(url, echo=echo, pool_pre_ping=True, pool_size=pool_size, max_overflow=10)
        self.session_factory = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)
    def session(self) -> AsyncSession: return self.session_factory()
    async def dispose(self) -> None: await self.engine.dispose()
