from fastapi import Request

from holonet.logging import get_correlation_id


def test_get_correlation_id_from_header():
    scope = {"type": "http", "headers": [(b"x-correlation-id", b"abc")]}
    request = Request(scope)
    assert get_correlation_id(request) == "abc"
