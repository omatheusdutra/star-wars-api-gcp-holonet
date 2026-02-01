from holonet.schemas.resources import ResourcePath


def test_resource_path_model():
    data = ResourcePath(resource_id=1)
    assert data.resource_id == 1
