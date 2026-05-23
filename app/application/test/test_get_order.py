import pytest

from app.application.use_cases.create_order import CreateOrderUseCase, OrderDTO
from app.application.use_cases.get_order import GetOrderUseCase
from app.infrastructure.mock_unit_of_work import InMemoryUnitOfWork


@pytest.mark.asyncio
async def test_get_order():
    # 1. In-memory UoW
    uow = InMemoryUnitOfWork()

    create_use_case = CreateOrderUseCase(uow)
    get_use_case = GetOrderUseCase(uow)

    # 2. создаём заказ
    order_data = OrderDTO(
        user_id="user-1",
        item_id="item-1",
        quantity=2,
        idempotency_key="c2088f6d-714d-4e8e-a88c-79bbd86c7f7f",
    )

    created_order = await create_use_case(order_data)

    # 3. получаем заказ
    fetched_order = await get_use_case(created_order.id)

    # 4. проверки
    assert fetched_order.id == created_order.id
    assert fetched_order.user_id == "user-1"
    assert fetched_order.quantity == 2
    assert fetched_order.item_id == "item-1"
    assert fetched_order.status == created_order.status
