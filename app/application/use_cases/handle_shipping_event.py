class HandleShippingEventUseCase:
    def __init__(self, unit_of_work):
        self._uow = unit_of_work

    async def __call__(self, event: dict):
        # # event_id = event["event_id"]
        # event_type = event["event_type"]
        # order_id = event["order_id"]
        # item_id = event["item_id"]
        # quantity = event["quantity"]
        # shipment_id = event["shipment_id"]

        # async with self._uow as uow:
        #     if await uow.inbox.exists(event_id):
        #         return

        #     await uow.inbox.create(

        #     )

        print(event)
