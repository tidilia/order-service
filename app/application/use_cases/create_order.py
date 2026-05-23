from pydantic import BaseModel

from app.core.models import EventTypeEnum, Order, OrderStatusEnum
from app.infrastructure.repositories.orders import OrderRepository
from app.infrastructure.repositories.outbox import OutboxRepository
from app.infrastructure.unit_of_work import UnitOfWork


class OrderDTO(BaseModel):
    """DTO для входных данных"""

    user_id: str
    quantity: int
    item_id: str
    idempotency_key: str


class CreateOrderUseCase:
    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work

    async def __call__(self, order: OrderDTO) -> Order:
        async with self._unit_of_work() as uow:
            key = order.idempotency_key
            if key:
                existing_order = await uow.orders.get_by_idempotency_key(key)
                if existing_order:
                    if (
                        existing_order.user_id != order.user_id
                        or existing_order.item_id != order.item_id
                        or existing_order.quantity != order.quantity
                    ):
                        raise ValueError(
                            "Order with the same idempotency key already exists"
                        )
                    return existing_order

            order = await uow.orders.create(
                OrderRepository.CreateDTO(
                    user_id=order.user_id,
                    quantity=order.quantity,
                    item_id=order.item_id,
                    status=OrderStatusEnum.NEW,
                    idempotency_key=key,
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
