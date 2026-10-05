from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from app.core.config import setting
from typing import AsyncGenerator

engine=create_async_engine(setting.DATABASE_URL,echo=True,future=True,pool_pre_ping=True,pool_size=10,max_overflow=20)

AsyncSessionLocal=async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    future=True,
)

# FastAPI Dependency
# This will be injected into your API endpoints
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session # Hand the session to the API endpoint
            # We don't automatically commit here; we let the Service layer handle commits/rollbacks
        finally:
            await session.close() # Always close the connection when done!