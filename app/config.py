from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:genbrdb123@localhost:5432/individuals"
    debug: bool = False
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
settings = Settings()
