from app.core.models import EventTypeEnum, OrderStatusEnum
from app.infrastructure.repositories.inbox import InboxRepository
from app.infrastructure.repositories.outbox import OutboxRepository


class HandleShippingEventUseCase:
    def __init__(self, unit_of_work, send_notification):
        self._uow = unit_of_work
        self._send_notification = send_notification

    async def __call__(self, event: dict):
        print(f"shipment event {event}")
        shipment_id = event["shipment_id"]
        event_type = event["event_type"]

        async with self._uow() as uow:
            if await uow.inbox.exists(shipment_id):
                return

            notif_message = ""
            notif_idempotency_key = ""

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
                notif_message = "Ваш заказ отправлен в доставку"
                notif_idempotency_key = f"{event["order_id"]}:shipped"

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
                notif_message = "Ваш заказ отменен. Причина: не удалось доставить"
                notif_idempotency_key = (f"{event["order_id"]}:cancelled",)

            await uow.commit()
            self._send_notification(
                message=notif_message,
                reference_id=str(event["order_id"]),
                iddempotency_key=notif_idempotency_key,
            )
