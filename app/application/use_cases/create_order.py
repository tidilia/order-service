import traceback
from decimal import Decimal

from fastapi import HTTPException
from pydantic import BaseModel

from app.application.interfaces import CatalogGateway
from app.core.models import EventTypeEnum, Order, OrderStatusEnum
from app.infrastructure.clients.payments_service import PaymentsServiceClient
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
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        catalog_client: CatalogGateway,
        payments_client: PaymentsServiceClient,
        send_notification,
    ):
        self._unit_of_work = unit_of_work
        self._catalog_client = catalog_client
        self._payments_client = payments_client
        self._send_notification = send_notification

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
                raise HTTPException(status_code=400, detail="Not enough items in stock")
            full_amount = item.price * order.quantity

            order = await uow.orders.create(
                OrderRepository.CreateDTO(
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
                OutboxRepository.CreateDTO(
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

            # 4. Коммит транзакции
            await uow.commit()

            self._send_notification(
                message="Ваш заказ создан и ожидает оплаты",
                reference_id=str(order.id),
                idempotency_key=f"{order.id}:new",
            )

            try:
                await self._payments_client.create_payment(
                    order_id=str(order.id),
                    amount=Decimal(order.amount),
                    idempotency_key=str(key),
                )
            except Exception as e:
                print("ERROR: ", e)
                print(traceback.format_exc())
                await uow.orders.update_status(order.id, OrderStatusEnum.CANCELLED)
                await uow.commit()
            return order
