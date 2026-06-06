from app.core.models import EventTypeEnum, OrderStatusEnum
from app.infrastructure.repositories.inbox import InboxRepository
from app.infrastructure.repositories.outbox import OutboxRepository


class HandleShippingEventUseCase:
    def __init__(
        self,
        unit_of_work,
    ):
        self._uow = unit_of_work

    async def __call__(self, event: dict):
        shipment_id = event["shipment_id"]
        event_type = event["event_type"]

        async with self._uow() as uow:
            if await uow.inbox.exists(shipment_id):
                return

            shipping_event = await uow.inbox.create(
                InboxRepository.CreateDTO(
                    item_id=event["item_id"],
                    order_id=event["order_id"],
                    quantity=event["quantity"],
                    event_type=event["event_type"],
                    shipment_id=event["shipment_id"],
                )
            )

            if event_type == EventTypeEnum.order_shipped:
                await uow.orders.update_status(
                    event["order_id"],
                    OrderStatusEnum.SHIPPED,
                )
                await uow.outbox.create(
                    OutboxRepository.CreateDTO(
                        event_type=EventTypeEnum.order_shipped,
                        payload=shipping_event.model_dump(mode="json"),
                    )
                )

            elif event_type == EventTypeEnum.order_cancelled:
                await uow.orders.update_status(
                    event["order_id"],
                    OrderStatusEnum.CANCELLED,
                )
                await uow.outbox.create(
                    OutboxRepository.CreateDTO(
                        event_type=EventTypeEnum.order_shipped,
                        payload=shipping_event.model_dump(mode="json"),
                    )
                )

            await uow.commit()
