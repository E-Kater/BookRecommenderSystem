from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from app.core.config import settings  # Your config file

# Database URL typically comes from your config
SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{settings.DB_USER}:{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/"
    f"{settings.DB_NAME}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# For async support (if needed)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

async_engine = create_async_engine(
    f"postgresql+asyncpg://"
    f"{settings.DB_USER}:{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/"
    f"{settings.DB_NAME}"
)

AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_async_db():
    """Async database session dependency"""
    async with AsyncSessionLocal() as db:
        yield db
