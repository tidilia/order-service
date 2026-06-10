from datetime import UTC, datetime

from pydantic import BaseModel
from sqlalchemy import insert, literal_column, select
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces import InboxRepositoryInterface
from app.core.models import EventTypeEnum, InboxEvent
from app.infrastructure.db.db_schema import inbox_tbl


class InboxRepository(InboxRepositoryInterface):
    class CreateDTO(BaseModel):
        item_id: str
        order_id: str
        quantity: int
        event_type: EventTypeEnum
        shipment_id: str

    def __init__(self, session: AsyncSession):
        self._session = session

    async def exists(self, shipment_id: str) -> bool:
        stmt = select(inbox_tbl.c.shipment_id).where(
            inbox_tbl.c.shipment_id == shipment_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def create(self, event: CreateDTO) -> InboxEvent:
        """Создание события в inbox"""
        stmt = (
            insert(inbox_tbl)
            .values(
                {
                    "order_id": event.order_id,
                    "shipment_id": event.shipment_id,
                    "event_type": event.event_type,
                    "payload": {
                        "item_id": event.item_id,
                        "quantity": event.quantity,
                    },
                    "processed": True,
                    "created_at": datetime.now(UTC),
                }
            )
            .returning(literal_column("*"))
        )
        result = await self._session.execute(stmt)
        row = result.fetchone()
        return self._construct(row)

    @staticmethod
    def _construct(row: Row) -> InboxEvent:
        """Преобразование строки БД в Domain модель"""
        return InboxEvent(
            id=str(row._mapping["id"]),
            order_id=str(row._mapping["order_id"]),
            shipment_id=str(row._mapping["shipment_id"]),
            event_type=row._mapping["event_type"],
            payload=row._mapping["payload"],
            processed=row._mapping["processed"],
            created_at=row._mapping["created_at"],
        )
