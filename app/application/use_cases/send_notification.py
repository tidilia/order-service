from app.infrastructure.clients.notifications_service import NotificationsServiceClient


class SendNotificationUseCase:
    def __init__(
        self,
        notifications_client: NotificationsServiceClient,
    ):
        self._notifications_client = notifications_client

    async def __call__(
        self,
        message: str,
        order_id: str,
        idempotency_key: str,
    ):
        try:
            await self._notifications_client.send_notification(
                message=message,
                reference_id=order_id,
                idempotency_key=idempotency_key,
            )
        except Exception as e:
            print(f"Notification error: {e}")
