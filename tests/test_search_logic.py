from holonet.schemas.search import SearchQuery
from holonet.services.search_service import SearchService


class FakeClient:
    def __init__(self):
        self.calls = []

    def search(self, resource, query, page):
        self.calls.append(page)
        if page == 1:
            return {
                "count": 3,
                "results": [
                    {"name": "Leia", "url": "https://swapi.dev/api/people/5/"},
                    {"name": "Luke", "url": "https://swapi.dev/api/people/1/"},
                ],
                "next": "page2",
                "_cache": {"hit": False, "ttl": 180},
            }
        return {
            "count": 3,
            "results": [
                {"name": "Anakin", "url": "https://swapi.dev/api/people/11/"},
            ],
            "next": None,
            "_cache": {"hit": False, "ttl": 180},
        }


def test_search_pagination_sort_fields():
    client = FakeClient()
    service = SearchService(client)

    query = SearchQuery(
        resource="people",
        q="",
        page=1,
        page_size=2,
        sort="name",
        order="asc",
        fields=["name", "id"],
    )
    items, pagination, _cache = service.search(query)

    assert [item["name"] for item in items] == ["Leia", "Luke"]
    assert pagination["total_items"] == 3
    assert "id" in items[0]
    assert set(items[0].keys()) == {"name", "id"}


def test_search_fetches_next_page_when_needed():
    client = FakeClient()
    service = SearchService(client)

    query = SearchQuery(resource="people", q="", page=1, page_size=3)
    items, pagination, _cache = service.search(query)

    assert client.calls == [1, 2]
    assert [item["name"] for item in items] == ["Leia", "Luke", "Anakin"]
    assert pagination["total_items"] == 3


def test_search_invalid_sort_field():
    client = FakeClient()
    service = SearchService(client)

    query = SearchQuery(
        resource="people", q="", page=1, page_size=2, sort="unknown_field", order="asc"
    )
    try:
        service.search(query)
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 400


class EmptyClient:
    def search(self, resource, query, page):
        return {"count": 1, "results": [], "next": None, "_cache": {"hit": False, "ttl": 180}}


def test_search_page_out_of_range():
    service = SearchService(EmptyClient())
    query = SearchQuery(resource="people", page=2, page_size=1)
    try:
        service.search(query)
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 404


class NoResultsClient:
    def search(self, resource, query, page):
        return {"count": 0, "results": [], "next": None, "_cache": {"hit": False, "ttl": 180}}


def test_search_no_results():
    service = SearchService(NoResultsClient())
    query = SearchQuery(resource="people", page=1, page_size=1)
    items, pagination, _cache = service.search(query)
    assert items == []
    assert pagination["total_items"] == 0


def test_search_extract_id_cases():
    from holonet.services.search_service import _extract_id

    assert _extract_id(None) is None
    assert _extract_id("") is None
    assert _extract_id("/people/") is None
    assert _extract_id("///") is None
    assert _extract_id("https://swapi.dev/api/people/abc/") is None


def test_search_all_paginates_and_sorts():
    class PagedClient:
        def __init__(self):
            self.pages = []

        def search(self, resource, query, page):
            self.pages.append(page)
            if page == 1:
                return {
                    "count": 3,
                    "results": [
                        {"name": "B", "url": "https://swapi.dev/api/people/2/"},
                        {"name": "A", "url": "https://swapi.dev/api/people/1/"},
                    ],
                    "next": "page2",
                    "_cache": {"hit": False, "ttl": 180},
                }
            return {
                "count": 3,
                "results": [
                    {"name": "C", "url": "https://swapi.dev/api/people/3/"},
                ],
                "next": None,
                "_cache": {"hit": False, "ttl": 180},
            }

    service = SearchService(PagedClient())
    query = SearchQuery(
        resource="people",
        q="",
        page=1,
        page_size=2,
        sort="name",
        order="asc",
        fields=["name", "id"],
    )
    items, pagination, _cache = service.search_all(query)

    assert [item["name"] for item in items] == ["A", "B", "C"]
    assert pagination["total_items"] == 3
    assert set(items[0].keys()) == {"name", "id"}


def test_search_all_invalid_sort_field():
    class SinglePageClient:
        def search(self, resource, query, page):
            return {
                "count": 1,
                "results": [{"name": "Luke", "url": "https://swapi.dev/api/people/1/"}],
                "next": None,
                "_cache": {"hit": False, "ttl": 180},
            }

    service = SearchService(SinglePageClient())
    query = SearchQuery(
        resource="people",
        q="",
        page=1,
        page_size=1,
        sort="invalid_field",
        order="asc",
        fields=["name"],
    )
    try:
        service.search_all(query)
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 400
