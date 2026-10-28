# Async Event Sourcing — SQLAlchemy + PostgreSQL

Exemplo de API assíncrona com `await application.save(...)`, `AsyncSession`, PostgreSQL/asyncpg, Event Store, projeção e Outbox transacional.

## Nota sobre `eventsourcing_sqlalchemy==1.0.1`

A versão upstream documenta a integração com `Session` síncrona e `recorder.transaction()` como context manager síncrono. Ela não expõe nativamente `AsyncSession`/`await Application.save()`. O projeto fixa essa dependência como referência, mas implementa um adaptador assíncrono próprio para não bloquear o event loop. Ele **não é drop-in replacement nem subclasse** do recorder síncrono upstream. A serialização e o modelo de eventos são explícitos neste exemplo.

## Executar

Requer Python 3.11+ e Docker.

```bash
docker compose up -d
python -m venv .venv
```

PowerShell:
```powershell
.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
pip install -e ".[test,rabbitmq]"
uvicorn app.main:app --reload
```

Linux/macOS:
```bash
source .venv/bin/activate
cp .env.example .env
pip install -e ".[test,rabbitmq]"
uvicorn app.main:app --reload
```

Swagger: http://127.0.0.1:8000/docs

As tabelas são criadas no startup apenas para facilitar o exemplo; em produção, use Alembic.

## Endpoints
- `POST /individuals` — cria indivíduo.
- `GET /individuals/{id}` — consulta projeção.
- `PATCH /individuals/{id}` — renomeia usando `expected_version`.
- `GET /individuals/{id}/events` — histórico de eventos.
- `GET /health` — health check.

## Uso programático

```python
async with application.unit_of_work() as uow:
    individual = Individual.create("Ana Silva")
    await application.save(individual, uow=uow)
    await uow.commit()
```

O commit confirma `stored_events`, `individuals` e `outbox_messages` na mesma transação. Exceção ou saída sem `commit()` provoca rollback. O registro na Outbox representa intenção de publicação; um worker RabbitMQ deve publicar com publisher confirms e marcar `PUBLISHED` após confirmação. A entrega é pelo menos uma vez, então consumidores devem ser idempotentes.

## Testes
```bash
pytest
```
O teste de domínio não exige PostgreSQL. Testes de integração reais precisam de PostgreSQL disponível.
