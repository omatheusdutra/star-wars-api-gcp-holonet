from fastapi import Request

from holonet import logging as log_utils


def test_log_json():
    log_utils.log_json("event_test", extra="x")


def test_get_correlation_id():
    scope = {"type": "http", "headers": []}
    request = Request(scope)
    cid = log_utils.get_correlation_id(request)
    assert cid
