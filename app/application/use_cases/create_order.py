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
    class CreateOrderCreatePaymentDTO(BaseModel):
        order_id: str
        amount: Decimal
        idempotency_key: str

    def __init__(
        self,
        unit_of_work: UnitOfWork,
        catalog_client: CatalogGateway,
        payments_client: PaymentsServiceClient,
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
                raise HTTPException(status_code=400, detail="Not enough items in stock")
            full_amount = item.price * order.quantity
            print(full_amount)

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
                    event_type=EventTypeEnum.ORDER_CREATED,
                    payload=order.model_dump(mode="json"),
                )
            )

            # 4. Коммит транзакции
            await uow.commit()

            print(self._payments_client)
            try:
                print("create order payment start")
                print(order)
                print(
                    f"order id {order.id}, amount {order.amount}, idempotency key {key}"
                )
                result = await self._payments_client.create_payment(
                    self.CreateOrderCreatePaymentDTO(
                        order_id=order.id, amount=order.amount, idempotency_key=key
                    )
                )
                print(result)
                print("create payment end")
            except Exception:
                await uow.orders.update_status(order.id, OrderStatusEnum.CANCELLED)
                await uow.commit()
            return order
