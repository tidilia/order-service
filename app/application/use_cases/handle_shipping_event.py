from app.application.interfaces import (
    InboxRepositoryInterface,
    OutboxRepositoryInterface,
)
from app.core.models import EventTypeEnum, OrderStatusEnum


class HandleShippingEventUseCase:
    def __init__(
        self,
        unit_of_work,
    ):
        self._uow = unit_of_work

    async def __call__(self, event: dict):
        print(f"HandleShippingEventUseCase: {event}")
        shipment_id = event["shipment_id"]
        event_type = event["event_type"]

        async with self._uow() as uow:
            if await uow.inbox.exists(shipment_id):
                return

            print(f"Creating inbox event for shipment_id: {shipment_id}")
            shipping_event = await uow.inbox.create(
                InboxRepositoryInterface.CreateDTO(
                    item_id=event["item_id"],
                    order_id=event["order_id"],
                    quantity=event["quantity"],
                    event_type=event["event_type"],
                    shipment_id=event["shipment_id"],
                )
            )
            print(f"Inbox event created: {shipping_event}")
            print("Changing order status based on shipping event")

            if event_type == EventTypeEnum.order_shipped:
                await uow.orders.update_status(
                    event["order_id"],
                    OrderStatusEnum.SHIPPED,
                )
                print("Order status updated to SHIPPED")
                print("Creating outbox event for order_shipped")
                await uow.outbox.create(
                    OutboxRepositoryInterface.CreateDTO(
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
                    OutboxRepositoryInterface.CreateDTO(
                        event_type=EventTypeEnum.order_cancelled,
                        payload=shipping_event.model_dump(mode="json"),
                    )
                )

            await uow.commit()
