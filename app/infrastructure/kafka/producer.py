import json

from aiokafka import AIOKafkaProducer

from app.application.interfaces import EventPublisher


class KafkaProducer(EventPublisher):
    def __init__(self, bootstrap_servers: str):
        self._bootstrap_servers = bootstrap_servers
        self._producer = None

    async def start(self):
        self._producer = AIOKafkaProducer(bootstrap_servers=self._bootstrap_servers)
        await self._producer.start()

    async def stop(self):
        await self._producer.stop()

    async def publish(
        self,
        topic: str,
        event: dict,
    ):
        await self._producer.send_and_wait(
            topic,
            json.dumps(event).encode(),
        )
