import asyncio
import logging
from datetime import datetime, timedelta, timezone

from app.core.models import EventTypeEnum
from app.infrastructure.clients.notifications_service import NotificationsServiceClient
from app.infrastructure.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class NotificationPublisher:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        notifications_client: NotificationsServiceClient,
        poll_interval: float = 2.0,
    ):
        self._uow = unit_of_work
        self._client = notifications_client
        self._poll_interval = poll_interval
        self._running = False

    async def start(self):
        self._running = True
        while self._running:
            try:
                await self.publish_pending()
            except Exception:
                logger.exception("Notification publisher loop failed")

            await asyncio.sleep(self._poll_interval)

    async def stop(self):
        self._running = False

    async def publish_pending(self):
        async with self._uow() as uow:
            events = await uow.outbox.get_notif_pending_events()

            for event in events:
                try:
                    if event.event_type == EventTypeEnum.order_created:
                        order_id = event.payload["id"]
                    else:
                        order_id = event.payload["order_id"]
                    idempotency_key = f"{order_id}:{str(event.event_type)}"

                    message = self._build_message(event.event_type)

                    response = await self._client.send_notification(
                        message=message,
                        reference_id=order_id,
                        idempotency_key=idempotency_key,
                    )

                    if event.created_at > datetime.now(timezone.utc) - timedelta(
                        minutes=10
                    ):
                        print(event)
                        print(response)

                    await uow.outbox.mark_as_sent_notif(event.id)

                except Exception:
                    logger.exception(
                        "Failed to send notification",
                        extra={
                            "event_id": str(event.id),
                            "event_type": str(event.event_type),
                        },
                    )

    def _build_message(self, event_type: EventTypeEnum) -> str:
        if event_type == EventTypeEnum.order_created:
            return "NEW Ваш заказ создан и ожидает оплаты"

        if event_type == EventTypeEnum.order_paid:
            return "PAID Ваш заказ успешно оплачен и готов к отправке"

        if event_type == EventTypeEnum.order_shipped:
            return "SHIPPED Ваш заказ отправлен в доставку"

        if event_type == EventTypeEnum.order_cancelled:
            return "CANCELLED Ваш заказ отменен"

        return "Уведомление по заказу"
