from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel


class OrderStatusEnum(StrEnum):
    NEW = "NEW"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


class PaymentStatusEnum(StrEnum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"


# class Item(BaseModel):
#     id: int
#     name: str
#     price: Decimal
#     available_qty: int
#     created_at: datetime


class Order(BaseModel):
    id: str
    user_id: str
    quantity: int
    item_id: str
    status: OrderStatusEnum
    created_at: datetime
    updated_at: datetime
    amount: Decimal
    idempotency_key: str
    # status_history:


class Payment(BaseModel):
    id: str
    order_id: str
    status: PaymentStatusEnum
    amount: Decimal
    created_at: datetime


# OutboxEvent, EventTypeEnum, OutboxEventStatus
class EventTypeEnum(StrEnum):
    order_created = "order.created"
    order_paid = "order.paid"
    order_shipped = "order.shipped"
    order_cancelled = "order.cancelled"


class OutboxEventStatus(StrEnum):
    PENDING = "PENDING"
    SENT = "SENT"


class OutboxEvent(BaseModel):
    id: str
    event_type: EventTypeEnum
    payload: dict
    status_kafka: OutboxEventStatus
    status_notification: OutboxEventStatus
    created_at: datetime


class InboxEvent(BaseModel):
    id: str
    order_id: str
    shipment_id: str
    event_type: EventTypeEnum
    payload: dict
    processed: bool
    created_at: datetime
