from fastapi import FastAPI

from app import config
from app.infrastructure.db.session import create_session_factory
from app.presentation.api.orders import router
from app.presentation.container import ApplicationContainer


def create_app():
    app = FastAPI()

    container = ApplicationContainer()

    session_factory = create_session_factory(
        db_url=config.DATABASE_URL,
    )

    # 3. ЗАПОЛНЯЕМ CONFIG
    container.config.from_dict(
        {"infrastructure": {"db": {"session_factory": session_factory}}}
    )

    container.wire(modules=["app.presentation.api.orders"])

    # 4. прикрепляем контейнер к app
    app.container = container
    app.include_router(router, prefix="/api")

    return app


app = create_app()
