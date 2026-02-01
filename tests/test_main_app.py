from importlib import reload

from holonet.errors import AppError


def test_root_route(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Holonet Galactic Console"


def test_auth_guard_enforced(monkeypatch):
    monkeypatch.setenv("REQUIRE_API_KEY", "true")
    monkeypatch.setenv("API_KEY", "secret")

    import holonet.config as cfg
    import holonet.main as main_mod

    reload(cfg)
    reload(main_mod)

    app = main_mod.create_app()
    c = app
    from fastapi.testclient import TestClient

    client = TestClient(c)
    resp = client.get("/v1/search?resource=people")
    assert resp.status_code == 401

    def fake_search(self, resource, query, page):
        return {"count": 0, "results": [], "next": None, "_cache": {"hit": False, "ttl": 180}}

    import holonet.clients.swapi_client as swapi_client

    monkeypatch.setattr(swapi_client.SwapiClient, "search", fake_search)

    resp = client.get("/v1/search?resource=people", headers={"x-api-key": "secret"})
    assert resp.status_code == 200

    monkeypatch.setenv("REQUIRE_API_KEY", "false")
    monkeypatch.setenv("API_KEY", "")
    reload(cfg)
    reload(main_mod)


def test_app_error_handler():
    import holonet.main as main_mod

    app = main_mod.create_app()

    @app.get("/boom")
    def _boom():
        raise AppError("boom", status_code=418)

    from fastapi.testclient import TestClient

    client = TestClient(app)
    resp = client.get("/boom")
    assert resp.status_code == 418
    assert resp.json()["error"]["message"] == "boom"
    assert resp.json()["correlation_id"]


def test_validation_error_envelope(client):
    resp = client.get("/v1/search?resource=people&page=0")
    assert resp.status_code == 422
    payload = resp.json()
    assert "error" in payload
    assert payload["error"]["status"] == 422
    assert payload["correlation_id"]


def test_http_exception_handler_includes_correlation_id():
    from fastapi import HTTPException
    from fastapi.testclient import TestClient

    import holonet.main as main_mod

    app = main_mod.create_app()

    @app.get("/forbidden")
    def _forbidden():
        raise HTTPException(status_code=403, detail="Forbidden")

    client = TestClient(app)
    resp = client.get("/forbidden")
    assert resp.status_code == 403
    payload = resp.json()
    assert payload["error"]["status"] == 403
    assert payload["correlation_id"]
