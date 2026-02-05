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
    environ = dict(request.environ)
    environ.setdefault("wsgi.input", BytesIO())
    environ.setdefault("REQUEST_METHOD", "GET")
    environ.setdefault("SERVER_NAME", "localhost")
    environ.setdefault("SERVER_PORT", "80")
    environ.setdefault("SERVER_PROTOCOL", "HTTP/1.1")
    environ.setdefault("wsgi.url_scheme", "http")
    environ.setdefault("QUERY_STRING", "")
    path = environ.get("PATH_INFO", "") or ""
    service = os.environ.get("K_SERVICE") or ""
    prefix = f"/{service}" if service else ""
    if prefix and path.startswith(prefix + "/"):
        environ["SCRIPT_NAME"] = prefix
        environ["PATH_INFO"] = path[len(prefix) :]

    return Response.from_app(wsgi_app, environ)


__all__ = ["app"]
