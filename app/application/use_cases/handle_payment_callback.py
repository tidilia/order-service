from decimal import Decimal

from pydantic import BaseModel

from app.core.models import EventTypeEnum, OrderStatusEnum, PaymentStatusEnum
from app.infrastructure.repositories.outbox import OutboxRepository
from app.infrastructure.unit_of_work import UnitOfWork


class PaymentCallbackDTO(BaseModel):
    payment_id: str
    order_id: str
    status: PaymentStatusEnum
    amount: Decimal
    error_message: str | None = None


class HandlePaymentCallbackUseCase:
    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work

    async def __call__(self, data: PaymentCallbackDTO):
        print(f"receive payment {data}")
        async with self._unit_of_work() as unit_of_work:
            order = await unit_of_work.orders.get_by_id(data.order_id)
            if (
                order.status == OrderStatusEnum.PAID
                and data.status == PaymentStatusEnum.SUCCEEDED
            ):
                return
            if data.status == PaymentStatusEnum.SUCCEEDED:
                await unit_of_work.orders.update_status(order.id, OrderStatusEnum.PAID)
                await unit_of_work.outbox.create(
                    OutboxRepository.CreateDTO(
                        event_type=EventTypeEnum.order_paid,
                        payload={
                            "event_type": EventTypeEnum.order_paid,
                            "order_id": order.id,
                            "item_id": order.item_id,
                            "quantity": order.quantity,
                            "idempotency_key": order.idempotency_key,
                        },
                    )
                )
            elif data.status == PaymentStatusEnum.FAILED:
                await unit_of_work.orders.update_status(
                    order.id, OrderStatusEnum.CANCELLED
                )

            await unit_of_work.commit()
