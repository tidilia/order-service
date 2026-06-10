from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from app.application.container import ApplicationContainer
from app.application.use_cases.create_order import CreateOrderUseCase, OrderDTO
from app.application.use_cases.get_order import GetOrderUseCase
from app.application.use_cases.handle_payment_callback import (
    HandlePaymentCallbackUseCase,
    PaymentCallbackDTO,
)
from app.core.exceptions import OutOfStockError
from app.core.models import Order

# from app.core.exceptions import OrderNotFoundError

router = APIRouter()


@router.post("/orders", status_code=status.HTTP_201_CREATED)
@inject
async def create_order(
    order: OrderDTO,
    create_order_use_case: CreateOrderUseCase = Depends(
        Provide[ApplicationContainer.create_order_use_case]
    ),
) -> Order:
    """Создание нового заказа"""
    try:
        return await create_order_use_case(order=order)
    except OutOfStockError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {str(e)}",
        )


@router.get("/orders/{order_id}", response_model=Order)
@inject
async def get_order(
    order_id: str,
    use_case: GetOrderUseCase = Depends(
        Provide[ApplicationContainer.get_order_use_case]
    ),
):
    order = await use_case(order_id)
    return order


@router.post("/orders/payment-callback")
@inject
async def payment_callback(
    data: PaymentCallbackDTO,
    use_case: HandlePaymentCallbackUseCase = Depends(
        Provide[ApplicationContainer.handle_payment_callback_use_case]
    ),
):
    await use_case(data)
    return {"ok": True}
