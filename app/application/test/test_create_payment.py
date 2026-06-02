from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.infrastructure.clients.payments_service import PaymentsServiceClient
from app.main import app


@pytest.mark.asyncio
async def test_create_order_calls_payments():
    # --- MOCK payments client ---
    mock_payments = AsyncMock(spec=PaymentsServiceClient)

    mock_payments.create_payment.return_value = {
        "id": "payment-1",
        "order_id": "order-1",
        "status": "pending",
        "amount": "100.00",
        "idempotency_key": "key-1",
    }

    # --- override container dependency ---
    container = app.container
    container.infrastructure.payments_client.override(lambda: mock_payments)

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/orders",
            json={
                "user_id": "user-1",
                "item_id": "item-1",
                "quantity": 1,
                "idempotency_key": "key-1",
            },
        )

    print(response.text)
    assert response.status_code == 201

    # --- проверяем, что платеж вызвался ---
    mock_payments.create_payment.assert_awaited_once()
