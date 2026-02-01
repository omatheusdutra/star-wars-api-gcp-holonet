import math


def build_pagination(page: int, page_size: int, total_items: int) -> dict[str, int | bool]:
    total_pages = max(1, math.ceil(total_items / page_size)) if page_size > 0 else 1
    return {
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }
