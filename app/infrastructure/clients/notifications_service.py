from urllib.parse import urljoin

import httpx


class NotificationsServiceClient:
    def __init__(self, base_url: str, api_key: str, http_client: httpx.AsyncClient):
        self.base_url = base_url
        self.api_key = api_key
        self.http_client = http_client

    async def send_notification(
        self,
        message: str,
        reference_id: str,
        idempotency_key: str,
    ):
        url = urljoin(self.base_url, "api/notifications")
        try:
            response = await self.http_client.post(
                url,
                headers={
                    "X-API-Key": self.api_key,
                },
                json={
                    "message": message,
                    "reference_id": reference_id,
                    "idempotency_key": idempotency_key,
                },
            )
            if response.status_code >= 400:
                return f"Notification failed {response.status_code} "

        except Exception as e:
            print(f"Notification service error: {e}")
            return None
