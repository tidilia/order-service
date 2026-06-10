from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.core.models import (
    EventTypeEnum,
    InboxEvent,
    Order,
    OrderStatusEnum,
    OutboxEvent,
)


class OrderRepositoryInterface(ABC):
    """Абстракция для работы с заказами"""

    class CreateDTO(BaseModel):
        user_id: str
        item_id: str
        quantity: int
        status: OrderStatusEnum
        idempotency_key: str
        amount: Decimal

    @abstractmethod
    async def create(self, order: CreateDTO) -> Order:
        """Создать заказ"""
        pass

    @abstractmethod
    async def get_by_id(self, order_id: str) -> Order:
        """Получить заказ по ID"""
        pass

    @abstractmethod
    async def get_by_idempotency_key(self, key: str):
        """Получить заказ по idempotency_key"""
        pass

    @abstractmethod
    async def update_status(self, order_id: str, status: OrderStatusEnum):
        pass


class OutboxRepositoryInterface(ABC):
    class CreateDTO(BaseModel):
        event_type: EventTypeEnum
        payload: dict

    @abstractmethod
    async def create(self, event: CreateDTO) -> OutboxEvent:
        pass

    @abstractmethod
    async def get_kafka_pending_events(self, limit: int = 100) -> list[OutboxEvent]:
        """Получение неотправленных kafka событий"""
        pass

    @abstractmethod
    async def mark_as_sent_kafka(self, event_id: str) -> None:
        """Пометить kafka событие как отправленное"""
        pass

    @abstractmethod
    async def get_notif_pending_events(self, limit: int = 100) -> list[OutboxEvent]:
        """Получение неотправленных событий"""
        pass

    @abstractmethod
    async def mark_as_sent_notif(self, event_id: str) -> None:
        """Пометить событие как отправленное"""
        pass


class InboxRepositoryInterface(ABC):
    class CreateDTO(BaseModel):
        item_id: str
        order_id: str
        quantity: int
        event_type: EventTypeEnum
        shipment_id: str

    @abstractmethod
    async def exists(self, shipment_id: str) -> bool:
        pass

    @abstractmethod
    async def create(self, event: CreateDTO) -> InboxEvent:
        pass


class CatalogGateway(ABC):
    @abstractmethod
    async def get_item(self, item_id: str) -> dict:
        pass


class EventPublisher(ABC):
    @abstractmethod
    async def publish(
        self,
        topic: str,
        event: dict,
    ) -> None:
        pass


class UnitOfWorkInterface(ABC):

    @abstractmethod
    def __call__(self) -> AbstractAsyncContextManager["UnitOfWorkSessionInterface"]:
        pass


class UnitOfWorkSessionInterface(ABC):

    @property
    @abstractmethod
    def orders(self) -> OrderRepositoryInterface:
        pass

    @property
    @abstractmethod
    def outbox(self) -> OutboxRepositoryInterface:
        pass

    @property
    @abstractmethod
    def inbox(self) -> InboxRepositoryInterface:
        pass

    @abstractmethod
    async def commit(self) -> None:
        pass


class PaymentsServiceClientInterface(ABC):
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

    @abstractmethod
    async def create_payment(
        self, order_id: str, amount: Decimal, idempotency_key: str
    ):
        pass
