from decimal import Decimal
from urllib.parse import urljoin

import httpx
import pytest

from app import config
from app.infrastructure.clients.payments_service import PaymentsServiceClient


@pytest.mark.asyncio
async def test_create_payment_real():
    base_url = config.CAPASHINO_URL
    api_key = config.LMS_API_KEY
    callback_url = urljoin(config.INTERNAL_SERVICE_URL, "/api/orders/payment-callback")
    async with httpx.AsyncClient() as http_client:
        client = PaymentsServiceClient(
            base_url=base_url,
            api_key=api_key,
            http_client=http_client,
            callback_url=callback_url,
        )

        response = await client.create_payment(
            order_id="test-order-123",
            amount=Decimal("50.00"),
            idempotency_key="test-key-123",
        )

        print(response)

        assert response.id is not None
