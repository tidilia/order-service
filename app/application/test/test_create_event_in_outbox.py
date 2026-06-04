import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app import config
from app.core.models import EventTypeEnum
from app.infrastructure.db.db_schema import Base, outbox_tbl
from app.main import create_app

engine = create_async_engine(config.DATABASE_URL, echo=False)

TestingSession = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


@pytest_asyncio.fixture
async def session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSession() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    app = create_app()
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_order_creates_outbox_event(
    client: AsyncClient,
    session,
):
    response = await client.post(
        "/api/orders",
        json={
            "user_id": "user_1",
            "quantity": 1,
            "item_id": "b236e92c-2143-4c47-afa3-2c06b1b8798b",
            "idempotency_key": "test-idem-key-123",
        },
    )

    assert response.status_code == 201

    # проверяем outbox
    result = await session.execute(outbox_tbl.select())
    events = result.fetchall()
    assert len(events) == 1
    event = events[0]

    assert event.event_type in [EventTypeEnum.order_created, EventTypeEnum.order_paid]
