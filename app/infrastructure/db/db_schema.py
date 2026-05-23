import uuid

from sqlalchemy import JSON, Column, DateTime, Integer, Table, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# metadata = MetaData()

orders_tbl = Table(
    "orders",
    Base.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("user_id", UUID(as_uuid=True), nullable=False),
    Column("item_id", UUID(as_uuid=True), nullable=False),
    Column("quantity", Integer, nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now()),
)

outbox_tbl = Table(
    "outbox",
    Base.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("event_type", Text, nullable=False),
    Column("payload", JSON, nullable=False),
    Column("status", Text, nullable=False),  # PENDING, SENT
    Column("created_at", DateTime, server_default=func.now()),
)
