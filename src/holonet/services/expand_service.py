from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from holonet.clients.swapi_client import SwapiClient
from holonet.config import settings
from holonet.errors import AppError
from holonet.logging import log_json


class ExpandService:
    def __init__(self, client: SwapiClient) -> None:
        self._client = client

    def expand_urls(self, urls: list[str]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        if not urls:
            return results
        with ThreadPoolExecutor(max_workers=settings.max_expand_concurrency) as executor:
            futures = {executor.submit(self._client.get_by_url, url): url for url in urls}
            for future in as_completed(futures):
                try:
                    data = future.result()
                    data.pop("_cache", None)
                    data["id"] = _extract_id(data.get("url"))
                    results.append(data)
                except AppError:
                    log_json("expand_failed", url=futures[future])
        return results


def _extract_id(url: str | None) -> int | None:
    if not url:
        return None
    parts = [p for p in url.split("/") if p]
    if not parts:
        return None
    try:
        return int(parts[-1])
    except ValueError:
        return None
