# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:2021Prismit$@localhost:5432/edangaldb"

settings = Settings()
