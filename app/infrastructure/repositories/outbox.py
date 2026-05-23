from datetime import UTC, datetime

from pydantic import BaseModel
from sqlalchemy import insert, literal_column
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import EventTypeEnum, OutboxEvent, OutboxEventStatus
from app.infrastructure.db.db_schema import outbox_tbl


class OutboxRepository:
    class CreateDTO(BaseModel):
        event_type: EventTypeEnum
        payload: dict

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, event: CreateDTO) -> OutboxEvent:
        """Создание события в outbox"""
        stmt = (
            insert(outbox_tbl)
            .values(
                {
                    "event_type": event.event_type,
                    "payload": event.payload,
                    "status": OutboxEventStatus.PENDING,  # Начальный статус
                    "created_at": datetime.now(UTC),
                }
            )
            .returning(literal_column("*"))
        )
        result = await self._session.execute(stmt)
        row = result.fetchone()
        return self._construct(row)

    @staticmethod
    def _construct(row: Row) -> OutboxEvent:
        """Преобразование строки БД в Domain модель"""
        return OutboxEvent(
            id=str(row._mapping["id"]),
            event_type=row._mapping["event_type"],
            payload=row._mapping["payload"],
            status=row._mapping["status"],
            created_at=row._mapping["created_at"],
        )
