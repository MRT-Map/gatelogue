from gatelogue_types import GatelogueData


def test_with_sources():
    GatelogueData.get_with_sources()
    assert True


def test_no_sources():
    GatelogueData.get_no_sources()
    assert True
