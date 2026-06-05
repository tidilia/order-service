import httpx
from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.clients.catalog_service import CatalogServiceClient
from app.infrastructure.clients.notifications_service import NotificationsServiceClient
from app.infrastructure.clients.payments_service import PaymentsServiceClient
from app.infrastructure.kafka.consumer import ShippingEventsConsumer
from app.infrastructure.kafka.producer import KafkaProducer
from app.infrastructure.kafka.publisher import OutboxPublisher
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

    http_client = providers.Singleton(
        httpx.AsyncClient,
    )

    catalog_client = providers.Factory(
        CatalogServiceClient,
        base_url=config.capashino_clients.base_url,
        api_key=config.api.api_key,
        http_client=http_client,
    )

    payments_client = providers.Factory(
        PaymentsServiceClient,
        base_url=config.capashino_clients.base_url,
        api_key=config.api.api_key,
        callback_url=config.payments.callback_url,
        http_client=http_client,
    )

    notifications_client = providers.Factory(
        NotificationsServiceClient,
        base_url=config.capashino_clients.base_url,
        api_key=config.api.api_key,
        http_client=http_client,
    )

    kafka_producer = providers.Singleton(
        KafkaProducer,
        bootstrap_servers=config.kafka.bootstrap_servers,
    )

    kafka_consumer = providers.Singleton(
        ShippingEventsConsumer,
        bootstrap_servers=config.kafka.bootstrap_servers,
        group_id="order-service-group",
    )

    outbox_publisher = providers.Singleton(
        OutboxPublisher, producer=kafka_producer, unit_of_work=unit_of_work
    )
