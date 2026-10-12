# fixture is basically dependency injection 
# fixture func is dependency and it is injected by passing the fixture func name in test-function , every time the depedency is injected new fresh dependency objected is ingested if scope is function

# so every test has new isolated dependency 
# but you can allow to use same dependency at different test by changing the scope of fixture


#  we are settig up the dependency of DB for testing 
from app import models
from app.database.session import get_db
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from app.models.common.base import Base
from app.main import app as fastapi_app
import os
from app.core.config import setting
from httpx import AsyncClient, ASGITransport
from sqlalchemy.pool import NullPool

TEST_DB_URL = os.getenv(
    "TEST_DATABASE_URL",
    setting.DATABASE_URL.rsplit("/", 1)[0] + "/test_series_test"
)

engine = create_async_engine(
    TEST_DB_URL,
    echo=False,
    poolclass=NullPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    class_= AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# fixture to create and drop tables for every test
# autouse=True means this runs automatically before every test , without calling for it ( we dont pass the fixture as argument in test function)


# we are setting up db for test , engine/connections is used for all db ddl operations and sessions are used for db transaction operations

@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield # before test , Base.metadata.create_all creates all the db tables and then this setup_db() stops and tests are runned and then below code is runned
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all) # all the tables dropped  , here we are usinf run_sync because Base.metadata.drop_all() is synchronous api but we are running through the async connection , so sqlalchemy provides run_sync func to run the sync function through async connection


# dependency of db sessions to our test
@pytest.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session


#fixture for HTTP client that simulates api to our client
@pytest.fixture
async def async_client(db_session):
    # we override the get_db dependency to test_get_db_dependency , because , when we call the api-endpoint for testing we do not pass any session obj in endpoint params , so by default it will call the our real-development /production session and so it will do perform operations on our development/production db , not the test db and we don't want that

    async def override_get_db():
        yield db_session

    fastapi_app.dependency_overrides[get_db] = override_get_db 

    transport = ASGITransport(app=fastapi_app) # ASGITransport lets httpx communicate fastapi app directly without network

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client # yields the client for for sending test requests

    # clears the overrides after the test is done
    fastapi_app.dependency_overrides.clear()






