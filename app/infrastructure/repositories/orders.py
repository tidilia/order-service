from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel
from sqlalchemy import insert, literal_column, select, update
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import Order, OrderStatusEnum, PaymentStatusEnum
from app.infrastructure.db.db_schema import orders_tbl


class OrderRepository:
    class CreateDTO(BaseModel):
        """DTO для создания заказа"""

        user_id: str
        item_id: str
        quantity: int
        status: OrderStatusEnum
        idempotency_key: str
        amount: Decimal

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
                    "idempotency_key": order.idempotency_key,
                    "amount": order.amount,
                }
            )
            .returning(literal_column("*"))
        )
        result = await self._session.execute(stmt)
        row = result.fetchone()

        # Преобразование в Domain модель
        return await self.get_by_id(row.id)

    async def get_by_idempotency_key(self, key: str):
        result = await self._session.execute(
            select(orders_tbl).where(orders_tbl.c.idempotency_key == key)
        )
        row = result.fetchone()
        if row:
            return self._construct(row)
        return None

    async def get_by_id(self, order_id: str) -> Order:
        """Получение заказа по ID"""
        stmt = self._get_order_query().where(orders_tbl.c.id == order_id)
        result = await self._session.execute(stmt)
        row = result.fetchone()

        if row is None:
            raise ValueError(f"Order with id {order_id} not found")

        # Преобразование из БД в Domain
        return self._construct(row)

    async def update_status(self, order_id: str, status: PaymentStatusEnum):
        stmt = (
            update(orders_tbl).where(orders_tbl.c.id == order_id).values(status=status)
        )

        await self._session.execute(stmt)

    @staticmethod
    def _construct(row: Row) -> Order:
        """Преобразование строки БД в Domain модель"""
        return Order(
            id=str(row._mapping["id"]),
            user_id=row._mapping["user_id"],
            quantity=row._mapping["quantity"],
            item_id=row._mapping["item_id"],
            status=OrderStatusEnum(row._mapping["status"]),
            created_at=row._mapping["created_at"],
            updated_at=row._mapping["updated_at"],
            amount=row._mapping["amount"],
            # status_history=row._mapping["status_history"] or [],
        )
