from uuid import UUID

from pydantic import BaseModel

from app.core.models import EventTypeEnum, Order, OrderStatusEnum
from app.infrastructure.repositories.orders import OrderRepository
from app.infrastructure.repositories.outbox import OutboxRepository
from app.infrastructure.unit_of_work import UnitOfWork


class OrderDTO(BaseModel):
    """DTO для входных данных"""

    user_id: str
    quantity: int
    item_id: UUID
    idempotency_key: UUID


class CreateOrderUseCase:
    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work

    async def __call__(self, order: OrderDTO) -> Order:
        async with self._unit_of_work() as uow:
            order = await uow.orders.create(
                OrderRepository.CreateDTO(
                    user_id=order.user_id,
                    quantity=order.quantity,
                    item_id=order.item_id,
                    status=OrderStatusEnum.NEW,
                )
            )

            # 3. Публикация события в outbox
            await uow.outbox.create(
                OutboxRepository.CreateDTO(
                    event_type=EventTypeEnum.ORDER_CREATED,
                    payload=order.model_dump(mode="json"),
                )
            )

            # 4. Коммит транзакции
            await uow.commit()
            return order
