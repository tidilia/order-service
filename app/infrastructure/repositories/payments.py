from sqlalchemy import insert, select

from app.application.interfaces import PaymentsRepositoryInterface
from app.infrastructure.db.db_schema import payments_tbl


class PaymentsRepository(PaymentsRepositoryInterface):

    def __init__(self, session):
        self._session = session

    async def exists(self, payment_id: str) -> bool:
        stmt = (
            select(payments_tbl.c.id)
            .where(payments_tbl.c.id == payment_id)
            .limit(1)
        )

        result = await self._session.execute(stmt)
        return result.scalar() is not None

    async def create(self, dto: PaymentsRepositoryInterface.CreateDTO) -> None:
        stmt = insert(payments_tbl).values(
            order_id=dto.order_id,
            status=dto.status,
            amount=dto.amount,
        )

        await self._session.execute(stmt)
