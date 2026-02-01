from holonet.errors import AppError
from holonet.services.expand_service import ExpandService


class FakeClient:
    def get_by_url(self, url):
        return {"name": "Luke", "url": url}


def test_expand_service_success():
    service = ExpandService(FakeClient())
    items = service.expand_urls(["https://swapi.dev/api/people/1/"])
    assert items[0]["name"] == "Luke"
    assert items[0]["id"] == 1


def test_expand_service_empty():
    service = ExpandService(FakeClient())
    assert service.expand_urls([]) == []


def test_expand_service_handles_error():
    class ErrorClient:
        def get_by_url(self, url):
            raise AppError("boom", status_code=502)

    service = ExpandService(ErrorClient())
    assert service.expand_urls(["https://swapi.dev/api/people/1/"]) == []


def test_expand_extract_id_cases():
    from holonet.services.expand_service import _extract_id

    assert _extract_id(None) is None
    assert _extract_id("") is None
    assert _extract_id("///") is None
    assert _extract_id("https://swapi.dev/api/people/abc/") is None
