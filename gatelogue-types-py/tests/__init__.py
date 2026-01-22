from gatelogue_types import GD
from gatelogue_types.air import AirAirline, AirAirport, AirFlight, AirGate
from gatelogue_types.bus import BusCompany, BusStop


def test_get():
    # gd = GD.get()
    # print(gd.timestamp, gd.version)
    assert True


def test_air_gate_merge():
    gd = GD.create(["0"])

    airport = AirAirport.create(gd.conn, 0, code="AAA")
    gate1 = AirGate.create(gd.conn, 0, airport=airport, code=None)
    gate2 = AirGate.create(gd.conn, 0, airport=airport, code="1", size="S")
    assert gd.conn.execute("SELECT count(rowid) FROM AirGate").fetchone()[0] == 2
    gate1.merge(gate2)
    assert gd.conn.execute("SELECT count(rowid) FROM AirGate").fetchone()[0] == 1


def test_air_flight_merge():
    gd = GD.create(["0", "1"])

    airline = AirAirline.create(gd.conn, 0, name="Example Air")
    airport1 = AirAirport.create(gd.conn, 0, code="AAA")
    airport2 = AirAirport.create(gd.conn, 0, code="BBB")
    gate1 = AirGate.create(gd.conn, 0, airport=airport1, code=None)
    gate2 = AirGate.create(gd.conn, 0, airport=airport2, code=None)
    gate3 = AirGate.create(gd.conn, 1, airport=airport1, code="A")
    gate4 = AirGate.create(gd.conn, 1, airport=airport2, code="B")
    flight1 = AirFlight.create(gd.conn, 0, airline=airline, code="001", from_=gate1, to=gate2)
    flight2 = AirFlight.create(gd.conn, 0, airline=airline, code="001", from_=gate3, to=gate4)
    assert gd.conn.execute("SELECT count(rowid) FROM AirFlight").fetchone()[0] == 2
    assert gd.conn.execute("SELECT count(rowid) FROM AirGate").fetchone()[0] == 4
    assert flight2 in flight1.equivalent_nodes()
    flight1.merge(flight2)
    assert gd.conn.execute("SELECT count(rowid) FROM AirFlight").fetchone()[0] == 1
    assert gd.conn.execute("SELECT count(rowid) FROM AirGate").fetchone()[0] == 2


def test_bus_stop_merge():
    gd = GD.create(["0", "1"])

    company = BusCompany.create(gd.conn, 0, name="Example Inc")
    stop1 = BusStop.create(gd.conn, 0, codes={"a", "b"}, company=company)
    stop2 = BusStop.create(gd.conn, 1, codes={"b", "c"}, company=company)
    assert stop2 in stop1.equivalent_nodes()
    stop1.merge(stop2)
