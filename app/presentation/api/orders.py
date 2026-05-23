from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from app.application.use_cases.create_order import CreateOrderUseCase, OrderDTO
from app.core.models import Order
from app.application.container import ApplicationContainer

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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {str(e)}",
        )
