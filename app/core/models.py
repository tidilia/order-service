from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class OrderStatusEnum(StrEnum):
    NEW = "NEW"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


# class Item(BaseModel):
#     id: int
#     name: str
#     price: Decimal
#     available_qty: int
#     created_at: datetime


class Order(BaseModel):
    id: int
    user_id: str
    quantity: int
    item_id: str
    status: OrderStatusEnum
    created_at: datetime
    updated_at: datetime
    # status_history:


# OutboxEvent, EventTypeEnum, OutboxEventStatus
class EventTypeEnum(StrEnum):
    ORDER_CREATED = "ORDER.CREATED"


class OutboxEventStatus(StrEnum):
    PENDING = "PENDING"
    SENT = "SENT"


class OutboxEvent(BaseModel):
    id: str
    event_type: EventTypeEnum
    payload: dict
    status: OutboxEventStatus
    created_at: datetime
