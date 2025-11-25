import os
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import AsyncGenerator

# PostgreSQL Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://ranex_user:ranex_password@localhost:5432/ranex_db"
)

# Async PostgreSQL URL
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Async Engine
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
    future=True,
    pool_pre_ping=True,
)

# Async Session Factory
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Sync Engine (for Alembic migrations)
sync_engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
)

# Sync Session Factory (for migrations)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Base Model
Base = declarative_base()


# Async Dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Sync Dependency (for compatibility)
def get_sync_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
