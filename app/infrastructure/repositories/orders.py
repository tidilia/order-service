from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import insert, literal_column, select
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import Order, OrderStatusEnum
from app.infrastructure.db.db_schema import orders_tbl


class OrderRepository:
    class CreateDTO(BaseModel):
        """DTO для создания заказа"""

        user_id: UUID
        item_id: UUID
        quantity: int
        status: OrderStatusEnum

    def __init__(self, session: AsyncSession):
        """Repository получает сессию БД"""
        self._session = session

    def _get_order_query(self):
        return select(orders_tbl)

    async def create(self, order: CreateDTO) -> Order:
        """Создание заказа в БД"""
        stmt = (
            insert(orders_tbl)
            .values(
                {
                    "user_id": order.user_id,
                    "item_id": order.item_id,
                    "quantity": order.quantity,
                    "status": order.status,
                    "created_at": datetime.now(UTC),
                    "updated_at": datetime.now(UTC),
                }
            )
            .returning(literal_column("*"))
        )
        result = await self._session.execute(stmt)
        row = result.fetchone()

        # Преобразование в Domain модель
        return await self.get_by_id(row.id)

    async def get_by_id(self, order_id: str) -> Order:
        """Получение заказа по ID"""
        stmt = self._get_order_query().where(orders_tbl.c.id == order_id)
        result = await self._session.execute(stmt)
        row = result.fetchone()

        if row is None:
            raise ValueError(f"Order with id {order_id} not found")

        # Преобразование из БД в Domain
        return self._construct(row)

    @staticmethod
    def _construct(row: Row) -> Order:
        """Преобразование строки БД в Domain модель"""
        return Order(
            id=str(row._mapping["id"]),
            user_id=UUID(row._mapping["user_id"]),
            quantity=row._mapping["quantity"],
            item_id=UUID(row._mapping["item_id"]),
            status=OrderStatusEnum(row._mapping["status"]),
            created_at=row._mapping["created_at"],
            updated_at=row._mapping["updated_at"],
            # status_history=row._mapping["status_history"] or [],
        )
