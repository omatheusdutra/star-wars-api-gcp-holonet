import os

from tests import conftest


def _restore_env(original_require, original_key):
    if original_require is None:
        os.environ.pop("REQUIRE_API_KEY", None)
    else:
        os.environ["REQUIRE_API_KEY"] = original_require
    if original_key is None:
        os.environ.pop("API_KEY", None)
    else:
        os.environ["API_KEY"] = original_key


def test_conftest_app_restores_env():
    original_require = os.environ.get("REQUIRE_API_KEY")
    original_key = os.environ.get("API_KEY")

    os.environ["REQUIRE_API_KEY"] = "true"
    os.environ["API_KEY"] = "secret"

    gen = conftest.app.__wrapped__()
    app_instance = next(gen)
    assert app_instance is not None
    assert os.environ["REQUIRE_API_KEY"] == "false"
    assert os.environ["API_KEY"] == ""

    try:
        next(gen)
    except StopIteration:
        pass

    assert os.environ["REQUIRE_API_KEY"] == "true"
    assert os.environ["API_KEY"] == "secret"

    _restore_env(original_require, original_key)


def test_conftest_app_restores_env_when_already_set():
    os.environ["REQUIRE_API_KEY"] = "preset"
    os.environ["API_KEY"] = "preset"

    gen = conftest.app.__wrapped__()
    next(gen)
    try:
        next(gen)
    except StopIteration:
        pass

    assert os.environ["REQUIRE_API_KEY"] == "preset"
    assert os.environ["API_KEY"] == "preset"

    _restore_env("preset", "preset")
    os.environ.pop("REQUIRE_API_KEY", None)
    os.environ.pop("API_KEY", None)
