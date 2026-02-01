import os
import sys

import json

from fastapi.testclient import TestClient
from werkzeug.wrappers import Response

ROOT = os.path.dirname(__file__)
SRC_PATH = os.path.join(ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from holonet.main import app as fastapi_app

client = TestClient(fastapi_app)


def _build_url(path: str, query_string: bytes) -> str:
    qs = query_string.decode() if query_string else ""
    if not qs:
        return path
    return f"{path}?{qs}"


def app(request):
    path = getattr(request, "path", "") or ""
    service = os.environ.get("K_SERVICE") or ""
    prefix = f"/{service}" if service else ""
    if prefix and path.startswith(prefix + "/"):
        path = path[len(prefix) :]
        request.environ["SCRIPT_NAME"] = prefix
        request.environ["PATH_INFO"] = path
    if path in ("/", "/health"):
        payload = {"status": "ok"}
        if path == "/":
            payload = {
                "name": "Holonet Galactic Console",
                "version": "v1",
                "status": "ok",
            }
        return Response(
            json.dumps(payload), status=200, content_type="application/json"
        )
    url = _build_url(path, getattr(request, "query_string", b""))
    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
    resp = client.request(request.method, url, headers=headers, data=request.get_data())
    return Response(
        resp.content,
        status=resp.status_code,
        headers=resp.headers,
        content_type=resp.headers.get("content-type"),
    )


__all__ = ["app"]
