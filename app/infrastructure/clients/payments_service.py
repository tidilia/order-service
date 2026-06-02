from datetime import datetime
from decimal import Decimal
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel


class PaymentsServiceClient:
    class RequestDTO(BaseModel):
        order_id: str
        amount: Decimal
        callback_url: str
        idempotency_key: str

    class ResponseDTO(BaseModel):
        id: str
        user_id: str
        order_id: str
        amount: Decimal
        status: str
        idempotency_key: str
        created_at: datetime

    def __init__(self, base_url: str, api_key: str, http_client: httpx.AsyncClient):
        self.base_url = base_url
        self.api_key = api_key
        self.http_client = http_client

    async def create_payment(
        self, data: "PaymentsServiceClient.RequestDTO"
    ) -> "PaymentsServiceClient.ResponseDTO":
        url = urljoin(self.base_url, f"api/payments/{data.order_id}")
        headers = {"X-API-Key": self.api_key}

        try:
            response = await self.http_client.post(
                url,
                headers=headers,
                json=data.model_dump(),
                timeout=10.0,
            )
            print(response.text)
            response.raise_for_status()
            return self.ResponseDTO.model_validate(response.json())

        except Exception:
            raise
