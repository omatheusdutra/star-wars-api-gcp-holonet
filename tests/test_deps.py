from holonet.deps import require_api_key


def test_require_api_key_no_enforcement(monkeypatch):
    monkeypatch.setenv("REQUIRE_API_KEY", "false")
    import importlib

    import holonet.config as cfg

    importlib.reload(cfg)

    assert require_api_key(x_api_key=None, api_key=None) is None


def test_require_api_key_unauthorized(monkeypatch):
    monkeypatch.setenv("REQUIRE_API_KEY", "true")
    monkeypatch.setenv("API_KEY", "secret")
    import importlib

    import holonet.config as cfg

    importlib.reload(cfg)

    try:
        require_api_key(x_api_key="bad", api_key=None)
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 401


def test_correlation_id_dependency():
    from fastapi import Request

    from holonet.deps import correlation_id_dependency

    scope = {"type": "http", "headers": []}
    request = Request(scope)
    request.state.correlation_id = "cid-123"
    assert correlation_id_dependency(request) == "cid-123"
