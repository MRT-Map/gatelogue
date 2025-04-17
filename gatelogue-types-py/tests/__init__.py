from gatelogue_types import GatelogueData


def test_with_sources():
    GatelogueData.get()
    assert True


def test_no_sources():
    GatelogueData.NS().get()
    assert True
