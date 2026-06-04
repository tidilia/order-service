from datetime import UTC, datetime

from pydantic import BaseModel
from sqlalchemy import insert, literal_column, select
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import EventTypeEnum, InboxEvent
from app.infrastructure.db.db_schema import inbox_tbl


class InboxRepository:
    class CreateDTO(BaseModel):
        event_id: str
        event_type: EventTypeEnum
        payload: dict

    def __init__(self, session: AsyncSession):
        self._session = session

    async def exists(self, event_id: str) -> bool:
        stmt = select(inbox_tbl.c.event_id).where(inbox_tbl.c.event_id == event_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def create(self, event: CreateDTO) -> InboxEvent:
        """Создание события в inbox"""
        stmt = (
            insert(inbox_tbl)
            .values(
                {
                    "event_id": event.event_id,
                    "event_type": event.event_type,
                    "payload": event.payload,
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
            event_id=str(row._mapping["event_id"]),
            event_type=row._mapping["event_type"],
            payload=row._mapping["payload"],
            processed=row._mapping["processed"],
            created_at=row._mapping["created_at"],
        )
