from holonet.utils.sorting import project_fields, safe_sort


def test_safe_sort_with_none_and_desc():
    items = [{"name": None}, {"name": "B"}, {"name": "A"}]
    sorted_items = safe_sort(items, "name", "desc")
    assert sorted_items[-1]["name"] is None


def test_project_fields_keeps_id():
    items = [{"id": 1, "name": "Luke", "height": "172"}]
    projected = project_fields(items, ["name"])
    assert projected[0]["name"] == "Luke"
    assert projected[0]["id"] == 1
