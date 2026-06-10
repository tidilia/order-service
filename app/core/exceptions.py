class OutOfStockError(Exception):
    def __init__(self, item_id: str):
        super().__init__(f"Item with id {item_id} is out of stock")
