from datetime import UTC, datetime

from app.core.models import Order, OutboxEvent, OutboxEventStatus
from app.infrastructure.repositories.orders import OrderRepository
from app.infrastructure.repositories.outbox import OutboxRepository


class InMemoryOrderRepository:
    """In-memory реализация для тестов"""

    def __init__(self):
        self._orders = {}
        self._orders_by_idempotency_key = {}
        self._next_id = 1

    async def create(self, order: OrderRepository.CreateDTO) -> Order:
        key = order.idempotency_key
        order_id = str(self._next_id)
        self._next_id += 1

        order = Order(
            id=order_id,
            user_id=order.user_id,
            item_id=order.item_id,
            quantity=order.quantity,
            status=order.status,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        self._orders[order_id] = order
        self._orders_by_idempotency_key[key] = order
        return order

    async def get_by_id(self, order_id: str) -> Order:
        if order_id not in self._orders:
            raise ValueError(f"Order {order_id} not found")
        return self._orders[order_id]

    async def get_by_idempotency_key(self, key: str):
        if key not in self._orders_by_idempotency_key:
            return None
        return self._orders_by_idempotency_key[key]


class InMemoryOutboxRepository:
    """In-memory реализация для тестов"""

    def __init__(self):
        self.events = []
        self._next_id = 1

    async def create(
        self,
        event: OutboxRepository.CreateDTO,
    ) -> OutboxEvent:

        outbox_event = OutboxEvent(
            id=str(self._next_id),
            event_type=event.event_type,
            payload=event.payload,
            status=OutboxEventStatus.PENDING,
            created_at=datetime.now(UTC),
        )

        self._next_id += 1

        self.events.append(outbox_event)

        return outbox_event
