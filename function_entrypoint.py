import asyncio
import os
import sys

from werkzeug.wrappers import Response

ROOT = os.path.dirname(__file__)
SRC_PATH = os.path.join(ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from holonet.main import app as fastapi_app


def _build_scope(request) -> dict:
    path = getattr(request, "path", "") or ""
    service = os.environ.get("K_SERVICE") or ""
    prefix = f"/{service}" if service else ""
    root_path = ""
    if prefix and path.startswith(prefix + "/"):
        root_path = prefix
        path = path[len(prefix) :]

    server_port = request.environ.get("SERVER_PORT") if hasattr(request, "environ") else None
    try:
        server_port = int(server_port) if server_port else 80
    except (TypeError, ValueError):
        server_port = 80

    headers = []
    for key, value in getattr(request, "headers", {}).items():
        headers.append((key.lower().encode("latin-1"), value.encode("latin-1")))

    return {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "3.0"},
        "http_version": request.environ.get("SERVER_PROTOCOL", "HTTP/1.1").split("/")[1]
        if hasattr(request, "environ")
        else "1.1",
        "method": getattr(request, "method", "GET"),
        "scheme": getattr(request, "scheme", "http"),
        "path": path,
        "query_string": getattr(request, "query_string", b"") or b"",
        "root_path": root_path,
        "server": (getattr(request, "host", "localhost").split(":")[0], server_port),
        "client": (getattr(request, "remote_addr", "") or "", 0),
        "headers": headers,
        "extensions": {},
    }


def app(request):
    body = request.get_data() if hasattr(request, "get_data") else b""
    scope = _build_scope(request)

    status_code = 500
    response_headers = []
    response_body = bytearray()

    async def receive():
        nonlocal body
        chunk = body
        body = b""
        return {"type": "http.request", "body": chunk, "more_body": False}

    async def send(message):
        nonlocal status_code, response_headers, response_body
        if message["type"] == "http.response.start":
            status_code = message["status"]
            response_headers = message.get("headers", [])
        elif message["type"] == "http.response.body":
            response_body.extend(message.get("body", b""))

    asyncio.run(fastapi_app(scope, receive, send))
    headers = {k.decode("latin-1"): v.decode("latin-1") for k, v in response_headers}
    return Response(bytes(response_body), status=status_code, headers=headers)


__all__ = ["app"]
