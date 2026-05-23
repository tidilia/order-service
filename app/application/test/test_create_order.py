from uuid import UUID

import pytest

from app.application.use_cases.create_order import CreateOrderUseCase, OrderDTO
from app.infrastructure.mock_unit_of_work import InMemoryUnitOfWork


@pytest.mark.asyncio
async def test_create_order():
    # Используем in-memory repository
    uow = InMemoryUnitOfWork()
    use_case = CreateOrderUseCase(uow)

    # Выполнение
    order_data = OrderDTO(
        user_id="8bd5c048-5c7d-4ca6-97a9-42db706c7783",
        item_id="4a141411-0871-4781-8b9c-8812ffdd1fba",
        quantity=2,
        idempotency_key="c2088f6d-714d-4e8e-a88c-79bbd86c7f7f",
    )
    order = await use_case(order_data)

    # Проверки
    assert order.id is not None
    assert order.user_id == UUID("8bd5c048-5c7d-4ca6-97a9-42db706c7783")
    assert len(uow.orders._orders) == 1
