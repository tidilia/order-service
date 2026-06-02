from dependency_injector import containers, providers

from app.application.use_cases.create_order import CreateOrderUseCase
from app.application.use_cases.get_order import GetOrderUseCase
from app.application.use_cases.handle_payment_callback import (
    HandlePaymentCallbackUseCase,
)


class ApplicationContainer(containers.DeclarativeContainer):

    infrastructure = providers.DependenciesContainer()
    config = providers.Configuration()

    create_order_use_case = providers.Factory(
        CreateOrderUseCase,
        unit_of_work=infrastructure.unit_of_work,
        catalog_client=infrastructure.catalog_client,
        payments_client=infrastructure.payments_client,
        callback_url=infrastructure.config.payments.callback_url,
    )

    get_order_use_case = providers.Factory(
        GetOrderUseCase,
        unit_of_work=infrastructure.unit_of_work,
    )

    handle_payment_callback_use_case = providers.Factory(
        HandlePaymentCallbackUseCase,
        unit_of_work=infrastructure.unit_of_work,
    )
