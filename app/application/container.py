from dependency_injector import containers, providers

from app.application.use_cases.create_order import CreateOrderUseCase
from app.application.use_cases.get_order import GetOrderUseCase


class ApplicationContainer(containers.DeclarativeContainer):

    infrastructure = providers.DependenciesContainer()

    create_order_use_case = providers.Factory(
        CreateOrderUseCase,
        unit_of_work=infrastructure.unit_of_work,
        catalog_client=infrastructure.catalog_client,
    )

    get_order_use_case = providers.Factory(
        GetOrderUseCase,
        unit_of_work=infrastructure.unit_of_work,
    )
