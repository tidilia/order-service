import json

from aiokafka import AIOKafkaConsumer
from app.config import SHIPMENT_EVENTS_TOPIC


class ShippingEventsConsumer:
    def __init__(self, bootstrap_servers: str, group_id: str):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.consumer = None

    async def start(self):
        self.consumer = AIOKafkaConsumer(
            SHIPMENT_EVENTS_TOPIC,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
        )
        await self.consumer.start()

    async def stop(self):
        await self.consumer.stop()

    async def listen(self, handler):
        async for msg in self.consumer:
            event = json.loads(msg.value.decode("utf-8"))
            await handler(event)
