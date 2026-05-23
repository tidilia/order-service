from urllib.parse import urljoin

import httpx


class CatalogServiceClient:
    def __init__(self, base_url: str, api_key: str, http_client: httpx.AsyncClient):
        self.base_url = base_url
        self.api_key = api_key
        self.http_client = http_client

    async def get_item(self, item_id: int):
        url = urljoin(self.base_url, f"/items/{item_id}")
        headers = {"X-API-Key": self.api_key}

        try:
            response = await self.http_client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()

        except Exception:
            raise
