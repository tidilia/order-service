from app.core.models import Order
from app.infrastructure.unit_of_work import UnitOfWork


class GetOrderUseCase:
    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work

    async def __call__(self, order_id: str) -> Order:
        async with self._unit_of_work() as uow:
            order = await uow.orders.get_by_id(order_id)
            return order
