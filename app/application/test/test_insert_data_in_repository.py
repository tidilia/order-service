import pytest

from app.application.use_cases.create_order import CreateOrderUseCase, OrderDTO
from app.config import DATABASE_URL
from app.infrastructure.db.session import create_session_maker
from app.infrastructure.unit_of_work import UnitOfWork


@pytest.fixture
def session_factory():
    return create_session_maker(DATABASE_URL)


@pytest.fixture
def uow(session_factory):
    return UnitOfWork(session_factory)


@pytest.mark.asyncio
async def test_create_order(uow):
    use_case = CreateOrderUseCase(uow)

    order_data = OrderDTO(
        user_id="user-1",
        item_id="4a141411-0871-4781-8b9c-8812ffdd1fba",
        quantity=2,
        idempotency_key="c2088f6d-714d-4e8e-a88c-79bbd86c7f7f",
    )

    order = await use_case(order_data)

    assert order.id is not None
    assert order.user_id == "user-1"
