def test_health_route(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["status"] == "ok"
    assert payload["source"]["name"] == "holonet"
    assert payload["cache"]["hit"] is False
    assert payload["correlation_id"]


def test_health_v1_route(client):
    resp = client.get("/v1/health")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["status"] == "ok"
    assert payload["source"]["name"] == "holonet"
    assert payload["cache"]["hit"] is False
    assert payload["correlation_id"]


def test_meta_route(client):
    resp = client.get("/v1/meta")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["name"] == "Holonet Galactic Console"
    assert payload["version"] == "v1"
    assert payload["source"]["name"] == "holonet"
    assert payload["cache"]["hit"] is False
    assert payload["correlation_id"]


def test_root_handler_direct():
    from holonet.routes import health as health_routes

    payload = health_routes.root(correlation_id="test-correlation")
    assert payload["message"] == "Luke, I am your father!"
    assert payload["correlation_id"] == "test-correlation"
