from gatelogue_types import GD, AirAirport, AirGate, AirAirline, AirFlight


def test_get():
    # gd = GD.get()
    # print(gd.timestamp, gd.version)
    assert True

def test_air_gate_merge():
    gd = GD.create(["0"])

    airport = AirAirport.create(gd.conn, 0, code="AAA")
    gate1 = AirGate.create(gd.conn, 0, airport=airport, code=None)
    gate2 = AirGate.create(gd.conn, 0, airport=airport, code="1", size="S")
    print(gd.conn.execute("SELECT * FROM AirGate").fetchall())
    gate1.merge(gate2)
    print(gd.conn.execute("SELECT * FROM AirGate").fetchall())

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
    print(gd.conn.execute("SELECT * FROM AirFlight").fetchall())
    print(gd.conn.execute("SELECT * FROM AirGate").fetchall())
    flight1.merge(flight2)
    print(gd.conn.execute("SELECT * FROM AirFlight").fetchall())
    print(gd.conn.execute("SELECT * FROM AirGate").fetchall())
