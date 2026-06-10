from decimal import Decimal

from pydantic import BaseModel

from app.application.interfaces import (
    CatalogGateway,
    OrderRepositoryInterface,
    OutboxRepositoryInterface,
    PaymentsServiceClientInterface,
    UnitOfWorkInterface,
)
from app.core.exceptions import OutOfStockError
from app.core.models import EventTypeEnum, Order, OrderStatusEnum


class OrderDTO(BaseModel):
    """DTO для входных данных"""

    user_id: str
    quantity: int
    item_id: str
    idempotency_key: str


class CreateOrderUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWorkInterface,
        catalog_client: CatalogGateway,
        payments_client: PaymentsServiceClientInterface,
    ):
        self._unit_of_work = unit_of_work
        self._catalog_client = catalog_client
        self._payments_client = payments_client

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

            item = await self._catalog_client.get_item(order.item_id)
            if item.available_qty < order.quantity:
                raise OutOfStockError(order.item_id)
            full_amount = item.price * order.quantity

            order = await uow.orders.create(
                OrderRepositoryInterface.CreateDTO(
                    user_id=order.user_id,
                    quantity=order.quantity,
                    item_id=order.item_id,
                    status=OrderStatusEnum.NEW,
                    idempotency_key=key,
                    amount=full_amount,
                )
            )

            # 3. Публикация события в outbox
            await uow.outbox.create(
                OutboxRepositoryInterface.CreateDTO(
                    event_type=EventTypeEnum.order_created,
                    payload={
                        "event_type": EventTypeEnum.order_created,
                        "order_id": str(order.id),
                        "item_id": order.item_id,
                        "quantity": order.quantity,
                        "idempotency_key": order.idempotency_key,
                    },
                )
            )

            try:
                await self._payments_client.create_payment(
                    order_id=str(order.id),
                    amount=Decimal(order.amount),
                    idempotency_key=str(key),
                )
            except Exception:
                await uow.orders.update_status(order.id, OrderStatusEnum.CANCELLED)
                await uow.commit()

            await uow.commit()
            return order
