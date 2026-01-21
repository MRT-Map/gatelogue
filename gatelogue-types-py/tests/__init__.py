from gatelogue_types import GD


def test_new_air():
    gd = GD.create(["source0", "source1"])
    print(gd.timestamp, gd.version)
    assert True
