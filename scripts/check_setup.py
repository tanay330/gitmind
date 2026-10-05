import httpx
from qdrant_client import QdrantClient
from gitmind.config import settings

client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
print("Qdrant collections:", client.get_collections())

r = httpx.get(
    "https://api.github.com/rate_limit",
    headers={"Authorization": f"Bearer {settings.github_token}"},
)
print("GitHub status:", r.status_code)
print("Rate limit:", r.json()["resources"]["core"])