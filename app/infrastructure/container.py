
from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from app.infrastructure.unit_of_work import UnitOfWork


class InfrastructureContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    # 1. Engine
    async_engine = providers.Singleton(
        create_async_engine,
        config.db.url,
        echo=False,
        pool_pre_ping=True,
    )

    # 2. Session factory
    session_factory = providers.Singleton(
        sessionmaker,
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # 3. Unit of Work
    unit_of_work = providers.Factory(
        UnitOfWork,
        session_factory=session_factory,
    )