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
    print(callback_url)
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

    return app


app = create_app()
