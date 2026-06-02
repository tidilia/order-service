from datetime import datetime
from decimal import Decimal
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel

from app.application.interfaces import CatalogGateway


class CatalogServiceClient(CatalogGateway):
    class CatalogItem(BaseModel):
        id: str
        name: str
        price: Decimal
        available_qty: int
        created_at: datetime

    def __init__(self, base_url: str, api_key: str, http_client: httpx.AsyncClient):
        self.base_url = base_url
        self.api_key = api_key
        self.http_client = http_client

    async def get_item(self, item_id: str):
        url = urljoin(self.base_url, f"api/catalog/items/{item_id}")
        headers = {"X-API-Key": self.api_key}

        try:
            response = await self.http_client.get(url, headers=headers)
            response.raise_for_status()
            return self.CatalogItem.model_validate(response.json())

        except Exception:
            raise
