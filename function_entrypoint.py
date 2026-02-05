import os
import sys
from io import BytesIO

from a2wsgi import ASGIMiddleware
from werkzeug.wrappers import Response

ROOT = os.path.dirname(__file__)
SRC_PATH = os.path.join(ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from holonet.main import app as fastapi_app

wsgi_app = ASGIMiddleware(fastapi_app)


def app(request):
    environ = dict(getattr(request, "environ", {}) or {})
    # Fill in missing WSGI keys for tests/mocks only.
    environ.setdefault("REQUEST_METHOD", getattr(request, "method", "GET"))
    environ.setdefault("SERVER_NAME", "localhost")
    environ.setdefault("SERVER_PORT", "80")
    environ.setdefault("SERVER_PROTOCOL", "HTTP/1.1")
    environ.setdefault("wsgi.url_scheme", "http")
    if "QUERY_STRING" not in environ:
        query_string = getattr(request, "query_string", b"")
        if isinstance(query_string, bytes):
            query_string = query_string.decode("utf-8", errors="ignore")
        environ["QUERY_STRING"] = query_string
    if "wsgi.input" not in environ:
        body = request.get_data() if hasattr(request, "get_data") else b""
        environ["wsgi.input"] = BytesIO(body)
        environ.setdefault("CONTENT_LENGTH", str(len(body)))

    path = environ.get("PATH_INFO", "") or ""
    service = os.environ.get("K_SERVICE") or ""
    prefix = f"/{service}" if service else ""
    if prefix and path.startswith(prefix + "/"):
        path = path[len(prefix) :]
        environ["SCRIPT_NAME"] = prefix
        environ["PATH_INFO"] = path

    return Response.from_app(wsgi_app, environ)


__all__ = ["app"]
