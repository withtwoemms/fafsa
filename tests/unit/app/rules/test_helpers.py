from app.rules import helpers


def test_get_by_path():
    data = {
        "a": {
            "b": {
                "c": 42
            },
            "d": [1, 2, 3]
        }
    }

    # Works (pure dict traversal)
    assert helpers.get_by_path(data, "a.b.c") == 42
    # Fails because the implementation CANNOT index lists → returns None
    assert helpers.get_by_path(data, "a.d.1") is None
    # Missing deeper keys → returns None (no default argument exists)
    assert helpers.get_by_path(data, "a.x.y") is None
    # Cannot go deeper than a primitive value → returns None
    assert helpers.get_by_path(data, "a.b.c.d") is None


def test_set_by_path():
    data = {}

    helpers.set_by_path(data, "x.y.z", 100)
    assert data == {"x": {"y": {"z": 100}}}

    helpers.set_by_path(data, "x.y.w", 200)
    assert data == {"x": {"y": {"z": 100, "w": 200}}}

    helpers.set_by_path(data, "a.b", [1, 2, 3])
    assert data == {"x": {"y": {"z": 100, "w": 200}}, "a": {"b": [1, 2, 3]}}
