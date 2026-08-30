import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# lien de connexion vers le conteneur Docker PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://pc_user:pc_password@localhost:5432/pc_db"
)

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

# fonction pour ouvrir ou fermé la connexion à la bd de façon asynchrone lors des requêtes
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
