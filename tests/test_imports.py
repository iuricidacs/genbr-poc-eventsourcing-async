def test_imports():
    from app.application.application import AsyncApplication
    from app.infrastructure.async_datastore import AsyncSQLAlchemyDatastore
    from app.infrastructure.async_recorder import AsyncApplicationRecorder
    assert AsyncApplication and AsyncSQLAlchemyDatastore and AsyncApplicationRecorder
