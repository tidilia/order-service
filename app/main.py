import asyncio
from urllib.parse import urljoin

from fastapi import FastAPI

from app import config
from app.application.container import ApplicationContainer
from app.infrastructure.container import InfrastructureContainer
from app.presentation.api.orders import router


def create_app():
    app = FastAPI()

    # 1. infrastructure container
    infra = InfrastructureContainer()
    callback_url = urljoin(config.INTERNAL_SERVICE_URL, "/api/orders/payment-callback")
    infra.config.from_dict(
        {
            "db": {
                "url": config.DATABASE_URL,
            },
            "capashino_clients": {
                "base_url": config.CAPASHINO_URL,
            },
            "api": {
                "api_key": config.LMS_API_KEY,
            },
            "payments": {
                "callback_url": callback_url,
            },
            "kafka": {
                "bootstrap_servers": config.KAFKA_BOOTSTRAP_SERVERS,
            },
        }
    )

    # 2. application container
    app_container = ApplicationContainer(
        infrastructure=infra,
    )

    # 3. DI wiring
    infra.wire(modules=["app.presentation.api.orders"])
    app_container.wire(modules=["app.presentation.api.orders"])

    # 4. attach
    app.container = app_container

    app.include_router(router, prefix="/api")

    @app.on_event("startup")
    async def startup():
        producer = app.container.kafka_producer()
        await producer.start()
        app.state.kafka_producer = producer

        publisher = infra.outbox_publisher()
        asyncio.create_task(publisher.run())

    @app.on_event("startup")
    async def start_consumer():
        consumer = infra.kafka_consumer()
        handler = app.container.handle_shipping_event_use_case()

        async def run():
            await consumer.start()
            await consumer.listen(handler)

        asyncio.create_task(run())

    return app


app = create_app()
