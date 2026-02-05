from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

# SQLAlchemy engine
# engine = create_engine(settings.DATABASE_URL, future=True)  # future=True → SQLAlchemy 2.x style
engine = create_engine(
    settings.DATABASE_URL,
    future=True,

    # 🔥 IMPORTANT POOL SETTINGS
    pool_size=20,
    max_overflow=40,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
)


# Session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
