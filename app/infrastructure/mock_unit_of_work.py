from app.infrastructure.repositories.mock_repositories import (
    InMemoryOrderRepository, InMemoryOutboxRepository)

# class InMemoryUnitOfWork:
#     def __init__(self):
#         self._orders = {}
#         self._outbox = []
#         self._committed = False

#     def __call__(self):
#         return self

#     async def __aenter__(self):
#         return _InMemoryUoWImplementation()

#     async def __aexit__(self, exc_type, exc_val, exc_tb):
#         if exc_type is None:
#             self._committed = True

# class _InMemoryUoWImplementation:
#     def __init__(self):
#         self.orders = InMemoryOrderRepository()
#         self.outbox = InMemoryOutboxRepository()

#     async def commit(self):
#         pass  # В памяти коммит не нужен


class InMemoryUnitOfWork:

    def __init__(self):
        self.orders = InMemoryOrderRepository()
        self.outbox = InMemoryOutboxRepository()
        self.committed = False

    def __call__(self):
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type is None:
            self.committed = True

    async def commit(self):
        self.committed = True
