# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # DATABASE_URL: str = "postgresql://postgres:2021Prismit$@localhost:5432/edangaldb"
    DATABASE_URL: str = "postgresql+psycopg2://edangaldb_user:ze30hAGOIKrHPA8sAupjHZmDGMkfKuOe@dpg-d3s6flq4d50c738ilg6g-a.oregon-postgres.render.com:5432/edangaldb"


settings = Settings()
