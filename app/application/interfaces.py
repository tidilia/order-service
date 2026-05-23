from abc import ABC, abstractmethod

from app.core.models import Order


class OrderRepository(ABC):
    """Абстракция для работы с заказами"""

    class CreateDTO(ABC):
        pass

    @abstractmethod
    async def create(self, order: CreateDTO) -> Order:
        """Создать заказ"""
        pass

    @abstractmethod
    async def get_by_id(self, order_id: str) -> Order:
        """Получить заказ по ID"""
        pass

    @abstractmethod
    async def update(self, order: Order) -> Order:
        """Обновить заказ"""
        pass
