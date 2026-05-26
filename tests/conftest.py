import pytest
import asyncio
from testcontainers.postgres import PostgresContainer
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from backend.database import Base, get_db
from backend.main import app as fastapi_app

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16-alpine") as postgres:
        conn_str = postgres.get_connection_url().replace("postgresql://", "postgresql+asyncpg://")
        yield conn_str

@pytest.fixture(scope="session")
async def db_engine(postgres_container):
    engine = create_async_engine(postgres_container)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture
async def db_session(db_engine):
    session_factory = async_sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session
        # Clean up tables after each test
        async with db_engine.begin() as conn:
            for table in reversed(Base.metadata.sorted_tables):
                await conn.execute(table.delete())

@pytest.fixture(autouse=True)
async def override_db(db_session):
    async def _get_db_override():
        yield db_session
    fastapi_app.dependency_overrides[get_db] = _get_db_override
    yield
    fastapi_app.dependency_overrides.clear()
