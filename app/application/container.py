from dependency_injector import containers, providers

from app.application.use_cases.create_order import CreateOrderUseCase


class ApplicationContainer(containers.DeclarativeContainer):

    infrastructure = providers.DependenciesContainer()

    create_order_use_case = providers.Factory(
        CreateOrderUseCase,
        unit_of_work=infrastructure.unit_of_work,
    )