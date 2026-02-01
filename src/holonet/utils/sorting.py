from typing import Any


def safe_sort(items: list[dict], key: str, order: str) -> list[dict]:
    reverse = order.lower() == "desc"

    def _key(item: dict) -> Any:
        value = item.get(key)
        if value is None:
            return "" if reverse else "~~~~"
        return value

    return sorted(items, key=_key, reverse=reverse)


def project_fields(items: list[dict], fields: list[str] | None) -> list[dict]:
    if not fields:
        return items
    selected = []
    for item in items:
        projected = {field: item.get(field) for field in fields if field in item}
        if "id" in item and "id" not in projected:
            projected["id"] = item["id"]
        selected.append(projected)
    return selected
