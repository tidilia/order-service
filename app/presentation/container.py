from dependency_injector import containers, providers

from app.application.use_cases.create_order import CreateOrderUseCase
from app.infrastructure.unit_of_work import UnitOfWork


class ApplicationContainer(containers.DeclarativeContainer):
    # Конфигурация
    config = providers.Configuration()

    # Unit of Work
    unit_of_work = providers.Factory(
        UnitOfWork,
        session_factory=config.infrastructure.db.session_factory,
    )

    # Use Cases
    create_order_use_case = providers.Factory(
        CreateOrderUseCase,
        unit_of_work=unit_of_work,
    )
