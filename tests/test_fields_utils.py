from holonet.utils.fields import parse_fields


def test_parse_fields():
    assert parse_fields("name,id, ,created") == ["name", "id", "created"]
    assert parse_fields("") is None
    assert parse_fields(None) is None
