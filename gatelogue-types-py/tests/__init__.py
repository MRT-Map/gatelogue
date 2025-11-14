from gatelogue_types import GatelogueData, GatelogueDataNS


def test_with_sources():
    GatelogueData.get()
    assert True


def test_no_sources():
    GatelogueDataNS.get()
    assert True
