import os
from importlib import reload

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def app():
    prev_require = os.environ.get("REQUIRE_API_KEY")
    prev_key = os.environ.get("API_KEY")
    os.environ["REQUIRE_API_KEY"] = "false"
    os.environ["API_KEY"] = ""

    import holonet.config as cfg
    import holonet.main as main_mod

    reload(cfg)
    reload(main_mod)
    app_instance = main_mod.create_app()

    yield app_instance

    if prev_require is None:
        os.environ.pop("REQUIRE_API_KEY", None)
    else:
        os.environ["REQUIRE_API_KEY"] = prev_require
    if prev_key is None:
        os.environ.pop("API_KEY", None)
    else:
        os.environ["API_KEY"] = prev_key


@pytest.fixture(scope="session")
def client(app):
    return TestClient(app)
