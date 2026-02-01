from __future__ import annotations

from collections import deque
from typing import Any

from holonet.clients.swapi_client import SwapiClient
from holonet.config import settings

RELATIONS = {
    "people": ["films", "homeworld", "species", "starships", "vehicles"],
    "films": ["characters", "planets", "starships", "vehicles", "species"],
    "planets": ["residents", "films"],
    "starships": ["films", "pilots"],
    "species": ["people", "films", "homeworld"],
    "vehicles": ["films", "pilots"],
}


class GraphService:
    def __init__(self, client: SwapiClient) -> None:
        self._client = client

    def build_graph(self, start_resource: str, start_id: int, depth: int) -> dict[str, Any]:
        max_depth = min(depth, settings.graph_max_depth)
        nodes: dict[str, dict[str, Any]] = {}
        edges: list[dict[str, Any]] = []
        visited: set[str] = set()

        queue: deque[tuple[str, int, int]] = deque()
        queue.append((start_resource, start_id, 0))

        while queue and len(nodes) < settings.graph_max_nodes:
            resource, resource_id, current_depth = queue.popleft()
            node_key = f"{resource}:{resource_id}"
            if node_key in visited:
                continue
            visited.add(node_key)

            data = self._client.get_resource(resource, resource_id)
            data["id"] = resource_id
            nodes[node_key] = {
                "id": node_key,
                "resource": resource,
                "label": data.get("name") or data.get("title") or node_key,
                "raw": _thin(data),
            }

            if current_depth >= max_depth:
                continue

            for key in RELATIONS.get(resource, []):
                value = data.get(key)
                if not value:
                    continue
                urls = value if isinstance(value, list) else [value]
                for url in urls:
                    rel_resource, rel_id = _parse_url(url)
                    if rel_resource and rel_id:
                        edges.append(
                            {"from": node_key, "to": f"{rel_resource}:{rel_id}", "type": key}
                        )
                        queue.append((rel_resource, rel_id, current_depth + 1))

        return {"nodes": list(nodes.values()), "edges": edges}


def _parse_url(url: str) -> tuple[str | None, int | None]:
    parts = [p for p in url.split("/") if p]
    if len(parts) < 2:
        return None, None
    resource = parts[-2]
    try:
        resource_id = int(parts[-1])
    except ValueError:
        return None, None
    return resource, resource_id


def _thin(data: dict[str, Any]) -> dict[str, Any]:
    keys = ["name", "title", "url", "created", "edited"]
    return {key: data.get(key) for key in keys if key in data}
