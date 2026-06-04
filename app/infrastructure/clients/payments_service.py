from datetime import datetime
from decimal import Decimal
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel


class PaymentsServiceClient:
    class RequestDTO(BaseModel):
        order_id: str
        amount: str
        idempotency_key: str
        callback_url: str

    class ResponseDTO(BaseModel):
        id: str
        user_id: str
        order_id: str
        amount: Decimal
        status: str
        idempotency_key: str
        created_at: datetime

    def __init__(
        self,
        base_url: str,
        callback_url: str,
        api_key: str,
        http_client: httpx.AsyncClient,
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.http_client = http_client
        self.callback_url = callback_url

    async def create_payment(
        self, order_id: str, amount: Decimal, idempotency_key: str
    ):
        url = urljoin(self.base_url, "api/payments")
        headers = {"X-API-Key": self.api_key}

        data = self.RequestDTO(
            order_id=order_id,
            amount=str(amount),
            idempotency_key=idempotency_key,
            callback_url=self.callback_url,
        )

        try:
            response = await self.http_client.post(
                url,
                headers=headers,
                json=data.model_dump(mode="json"),
                timeout=10.0,
            )
            response.raise_for_status()
            return self.ResponseDTO.model_validate(response.json())

        except Exception:
            raise
