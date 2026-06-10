import uuid

from sqlalchemy import (JSON, Boolean, Column, DateTime, Integer, Numeric,
                        Table, Text, func)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# metadata = MetaData()

orders_tbl = Table(
    "orders",
    Base.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("user_id", Text, nullable=False),
    Column("item_id", Text, nullable=False),
    Column("quantity", Integer, nullable=False),
    Column("status", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column(
        "updated_at",
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    ),
    Column("idempotency_key", Text, nullable=True, unique=True),
    Column("amount", Numeric(10, 2), nullable=False),
)

outbox_tbl = Table(
    "outbox",
    Base.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("event_type", Text, nullable=False),
    Column("payload", JSON, nullable=False),
    Column("status_kafka", Text, nullable=False),  # PENDING, SENT
    Column("status_notification", Text, nullable=False),  # PENDING, SENT
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

inbox_tbl = Table(
    "inbox",
    Base.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("order_id", Text, nullable=False),
    Column("shipment_id", Text, nullable=False, unique=True),
    Column("event_type", Text, nullable=False),
    Column("payload", JSON, nullable=False),
    Column("processed", Boolean, default=False),
    Column("created_at", DateTime(timezone=True)),
)
