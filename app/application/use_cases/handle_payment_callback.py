from decimal import Decimal

from pydantic import BaseModel

from app.core.models import OrderStatusEnum, PaymentStatusEnum
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
        async with self._unit_of_work as unit_of_work:
            order = unit_of_work.orders.get_by_id(data.order_id)
            if (
                order.status == OrderStatusEnum.PAID
                and data.status == PaymentStatusEnum.SUCCEEDED
            ):
                return
            if data.status == PaymentStatusEnum.SUCCEEDED:
                await unit_of_work.orders.update_status(order.id, OrderStatusEnum.PAID)
            elif data.status == PaymentStatusEnum.FAILED:
                await unit_of_work.orders.update_status(
                    order.id, OrderStatusEnum.CANCELLED
                )

            await unit_of_work.commit()
