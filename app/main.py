import uvicorn
from contextlib import asynccontextmanager
from uuid import UUID, uuid4
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.application import AsyncApplication
from app.db import Base, engine, get_session
from app.domain.individual import Individual
from app.infrastructure.models import StoredEventRecord
from app.schemas import CreateIndividualRequest, IndividualResponse, RenameIndividualRequest, StoredEventResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn: await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(title="Individual Async Event Sourcing", version="0.1.0", lifespan=lifespan)

@app.get("/health")
async def health(): return {"status":"ok"}

@app.post("/individuals", response_model=IndividualResponse, status_code=201)
async def create(body: CreateIndividualRequest, session: AsyncSession = Depends(get_session)):
    application = AsyncApplication(session)
    #aggregate = Individual.create(body.name)
    aggregate = Individual(id=uuid4(), name=body.name)
    async with application.unit_of_work() as uow:
        await application.save(aggregate, uow=uow); await uow.commit()
    return await application.get_projection(aggregate.id)

@app.get("/individuals/{individual_id}", response_model=IndividualResponse)
async def get_one(individual_id: UUID, session: AsyncSession = Depends(get_session)):
    return await AsyncApplication(session).get_projection(individual_id)

@app.patch("/individuals/{individual_id}", response_model=IndividualResponse)
async def rename(individual_id: UUID, body: RenameIndividualRequest, session: AsyncSession = Depends(get_session)):
    application = AsyncApplication(session)
    async with application.unit_of_work() as uow:
        aggregate = await application.get(individual_id)
        if aggregate.version != body.expected_version:
            raise HTTPException(status_code=409, detail={"message":"Versão desatualizada", "current_version":aggregate.version})
        aggregate.rename(body.name)
        await application.save(aggregate, uow=uow); await uow.commit()
    return await application.get_projection(individual_id)

@app.get("/individuals/{individual_id}/events", response_model=list[StoredEventResponse])
async def events(individual_id: UUID, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(StoredEventRecord).where(StoredEventRecord.aggregate_id == individual_id).order_by(StoredEventRecord.aggregate_version))
    return list(result.scalars().all())

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)