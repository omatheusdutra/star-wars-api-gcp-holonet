import json
import os
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


class FakeRequest:
    def __init__(self, path: str, method: str = "GET", query_string: bytes = b"", headers=None):
        self.path = path
        self.method = method
        self.query_string = query_string
        self.headers = headers or {}
        self.environ = {"PATH_INFO": path, "SCRIPT_NAME": ""}

    def get_data(self):
        return b""


def _parse_response(resp):
    return json.loads(resp.get_data(as_text=True))


def _load_module(path: Path, name: str):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    assert spec and spec.loader
    root = str(path.parent)
    sys.path.insert(0, root)
    try:
        spec.loader.exec_module(module)
    finally:
        if sys.path and sys.path[0] == root:
            sys.path.pop(0)
    return module


def test_root_main_entrypoint_health():
    root = Path(__file__).resolve().parents[1]
    entry = _load_module(root / "main.py", "holonet_root_main")

    resp = entry.app(FakeRequest("/health"))
    assert resp.status_code == 200
    payload = _parse_response(resp)
    assert payload["status"] == "ok"


def test_root_main_entrypoint_v1_health_with_prefix():
    root = Path(__file__).resolve().parents[1]
    entry = _load_module(root / "main.py", "holonet_root_main_prefix")

    os.environ["K_SERVICE"] = "holonet-api"
    try:
        resp = entry.app(FakeRequest("/holonet-api/v1/health"))
        assert resp.status_code == 200
        payload = _parse_response(resp)
        assert payload["status"] == "ok"
        assert payload["correlation_id"]
    finally:
        os.environ.pop("K_SERVICE", None)


def test_function_entrypoint_v1_meta():
    root = Path(__file__).resolve().parents[1]
    entry = _load_module(root / "function_entrypoint.py", "holonet_function_entry")

    resp = entry.app(FakeRequest("/v1/meta"))
    assert resp.status_code == 200
    payload = _parse_response(resp)
    assert payload["name"] == "Holonet Galactic Console"
    assert payload["correlation_id"]
