from app.application.interfaces import UnitOfWorkInterface
from app.core.models import Order


class GetOrderUseCase:
    def __init__(self, unit_of_work: UnitOfWorkInterface):
        self._unit_of_work = unit_of_work

    async def __call__(self, order_id: str) -> Order:
        async with self._unit_of_work() as uow:
            order = await uow.orders.get_by_id(order_id)
            return order
