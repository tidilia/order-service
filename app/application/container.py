from dependency_injector import containers, providers

from app.application.use_cases.create_order import CreateOrderUseCase
from app.application.use_cases.get_order import GetOrderUseCase
from app.application.use_cases.handle_payment_callback import (
    HandlePaymentCallbackUseCase,
)
from app.application.use_cases.handle_shipping_event import HandleShippingEventUseCase


class ApplicationContainer(containers.DeclarativeContainer):

    infrastructure = providers.DependenciesContainer()

    create_order_use_case = providers.Factory(
        CreateOrderUseCase,
        unit_of_work=infrastructure.unit_of_work,
        catalog_client=infrastructure.catalog_client,
        payments_client=infrastructure.payments_client,
    )

    get_order_use_case = providers.Factory(
        GetOrderUseCase,
        unit_of_work=infrastructure.unit_of_work,
    )

    handle_payment_callback_use_case = providers.Factory(
        HandlePaymentCallbackUseCase,
        unit_of_work=infrastructure.unit_of_work,
    )

    handle_shipping_event_use_case = providers.Factory(
        HandleShippingEventUseCase,
        unit_of_work=infrastructure.unit_of_work,
    )
