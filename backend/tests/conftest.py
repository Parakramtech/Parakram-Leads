"""Shared fixtures for the test suite."""

import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://sigma:sigma@postgres:5432/sigma_leads_test",
)

def pytest_configure(config):
    config.option.asyncio_mode = "auto"


@pytest_asyncio.fixture()
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Create fresh DB tables for each test and tear them down afterwards."""
    from app.database import Base

    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture()
async def async_client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """HTTPX async client that overrides the get_db dependency with the test DB."""
    from app.database import get_db
    from app.main import app

    async def _override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture()
async def test_user(test_db: AsyncSession):
    """Create a test admin user."""
    from app.models.user import User
    from app.utils.security import hash_password

    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        hashed_password=hash_password("testpassword123"),
        full_name="Test User",
        role="admin",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    test_db.add(user)
    await test_db.flush()
    return user


@pytest_asyncio.fixture()
async def test_organization(test_db: AsyncSession, test_user):
    """Create a test organization with the test_user as ADMIN member."""
    from app.models.organization import Organization, UserOrganization, OrgRole

    org = Organization(
        id=uuid.uuid4(),
        name="Test Organization",
        slug="test-org",
        is_active=True,
        settings={},
        max_users=5,
        max_leads=500,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    test_db.add(org)
    await test_db.flush()

    membership = UserOrganization(
        user_id=test_user.id,
        organization_id=org.id,
        role=OrgRole.ADMIN,
        is_active=True,
        joined_at=datetime.now(timezone.utc),
    )
    test_db.add(membership)
    await test_db.flush()
    return org


@pytest_asyncio.fixture()
async def auth_headers(test_user):
    """Generate a JWT token for the test user and return Authorization headers."""
    from app.utils.security import create_access_token

    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def mock_openai():
    """Patch httpx.AsyncClient used by ai_analyzer to avoid real API calls."""
    with patch("app.services.ai_analyzer.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{"analysis": "mocked"}'}}]
        }
        mock_client.post = AsyncMock(return_value=mock_response)
        yield mock_client


@pytest.fixture()
def mock_sendgrid():
    """Patch SendGridAPIClient to avoid real email sends."""
    with patch("app.services.email_service.SendGridAPIClient") as mock_cls:
        mock_sg = MagicMock()
        mock_cls.return_value = mock_sg
        mock_sg.send.return_value = MagicMock(status_code=202)
        yield mock_sg


@pytest.fixture()
def mock_redis():
    """Patch redis.asyncio.from_url to avoid real Redis connections."""
    with patch("redis.asyncio.from_url") as mock_from_url:
        mock_conn = AsyncMock()
        mock_from_url.return_value = mock_conn
        yield mock_conn
