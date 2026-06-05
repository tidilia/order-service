from datetime import UTC, datetime

from pydantic import BaseModel
from sqlalchemy import insert, literal_column, select
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
                    "status_notification": OutboxEventStatus.PENDING,
                    "status_kafka": OutboxEventStatus.PENDING,  # Начальный статус
                    "created_at": datetime.now(UTC),
                }
            )
            .returning(literal_column("*"))
        )
        result = await self._session.execute(stmt)
        row = result.fetchone()
        return self._construct(row)

    async def get_kafka_pending_events(self, limit: int = 100) -> list[OutboxEvent]:
        """Получение неотправленных событий"""
        stmt = (
            select(outbox_tbl)
            .where(outbox_tbl.c.status_kafka == OutboxEventStatus.PENDING)
            .order_by(outbox_tbl.c.created_at)  # Старые события первыми
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        rows = result.fetchall()
        return [self._construct(row) for row in rows]

    async def mark_as_sent_kafka(self, event_id: str) -> None:
        """Пометить событие как отправленное"""
        stmt = (
            outbox_tbl.update()
            .where(outbox_tbl.c.id == event_id)
            .values(status_kafka=OutboxEventStatus.SENT)
        )
        await self._session.execute(stmt)

    async def get_notif_pending_events(self, limit: int = 100) -> list[OutboxEvent]:
        """Получение неотправленных событий"""
        stmt = (
            select(outbox_tbl)
            .where(outbox_tbl.c.status_notification == OutboxEventStatus.PENDING)
            .order_by(outbox_tbl.c.created_at)  # Старые события первыми
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        rows = result.fetchall()
        return [self._construct(row) for row in rows]

    async def mark_as_sent_notif(self, event_id: str) -> None:
        """Пометить событие как отправленное"""
        stmt = (
            outbox_tbl.update()
            .where(outbox_tbl.c.id == event_id)
            .values(status_notification=OutboxEventStatus.SENT)
        )
        await self._session.execute(stmt)

    @staticmethod
    def _construct(row: Row) -> OutboxEvent:
        """Преобразование строки БД в Domain модель"""
        return OutboxEvent(
            id=str(row._mapping["id"]),
            event_type=row._mapping["event_type"],
            payload=row._mapping["payload"],
            status_kafka=row._mapping["status_kafka"],
            status_notification=row._mapping["status_notification"],
            created_at=row._mapping["created_at"],
        )
