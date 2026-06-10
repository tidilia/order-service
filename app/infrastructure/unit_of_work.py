from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.interfaces import UnitOfWorkInterface, UnitOfWorkSessionInterface
from app.infrastructure.repositories.inbox import InboxRepository
from app.infrastructure.repositories.orders import OrderRepository
from app.infrastructure.repositories.outbox import OutboxRepository
from app.infrastructure.repositories.payments import PaymentsRepository


class UnitOfWork(UnitOfWorkInterface):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    @asynccontextmanager
    async def __call__(self):
        async with self._session_factory() as session:
            try:
                yield _UnitOfWorkImplementation(session)
                await session.rollback()
            except Exception:
                await session.rollback()
                raise


class _UnitOfWorkImplementation(UnitOfWorkSessionInterface):

    def __init__(self, session: AsyncSession):
        self._session = session
        self._order_repo = OrderRepository(session)
        self._outbox_repo = OutboxRepository(session)
        self._inbox_repo = InboxRepository(session)
        self._payments_repo = PaymentsRepository(session)

    @property
    def orders(self) -> OrderRepository:
        return self._order_repo

    @property
    def outbox(self) -> OutboxRepository:
        return self._outbox_repo

    @property
    def inbox(self) -> InboxRepository:
        return self._inbox_repo

    @property
    def payments(self) -> PaymentsRepository:
        return self._payments_repo

    async def commit(self):
        await self._session.commit()
