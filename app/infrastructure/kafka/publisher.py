import asyncio

from app.config import ORDER_EVENTS_TOPIC


class OutboxPublisher:
    def __init__(
        self,
        producer,
        unit_of_work,
    ):
        self._producer = producer
        self._unit_of_work = unit_of_work

    async def publish_pending(self):
        async with self._unit_of_work() as uow:
            events = await uow.outbox.get_pending_events()

            for event in events:
                await self._producer.publish(
                    topic=ORDER_EVENTS_TOPIC,
                    event=event.payload,
                )
                await uow.outbox.mark_as_sent(event.id)

            await uow.commit()

    async def run(self):
        while True:
            await self.publish_pending()
            await asyncio.sleep(5)
