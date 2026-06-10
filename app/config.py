import os

EVENTS_PROVIDER_URL = os.getenv("EVENTS_PROVIDER_URL")
LMS_API_KEY = os.getenv("LMS_API_KEY")
CAPASHINO_URL = os.getenv("CAPASHINO_URL")
SENTRY_DSN = os.getenv("SENTRY_DSN")
DATABASE_URL = os.getenv("POSTGRES_CONNECTION_STRING")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
INTERNAL_SERVICE_URL = os.getenv("INTERNAL_SERVICE_URL")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
ORDER_EVENTS_TOPIC = "student_system-order.events"
SHIPMENT_EVENTS_TOPIC = "student_system-shipment.events"
