BEGIN;

CREATE TABLE Source
(
    priority INTEGER PRIMARY KEY,
    name     TEXT
) STRICT;

CREATE TABLE Node
(
    i    INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL CHECK ( type IN ('AirAirline', 'AirAirport', 'AirGate', 'AirFlight',
                                        'BusCompany', 'BusLine', 'BusStop', 'BusBerth', 'BusConnection',
                                        'SeaCompany', 'SeaLine', 'SeaStop', 'SeaDock', 'SeaConnection',
                                        'RailCompany', 'RailLine', 'RailStation', 'RailPlatform', 'RailConnection',
                                        'Town', 'SpawnWarp') )
) STRICT;
CREATE TABLE NodeSource
(
    i      INTEGER NOT NULL REFERENCES Node (i),
    source INTEGER NOT NULL REFERENCES Source (priority),
    PRIMARY KEY (i, source)
) STRICT;

CREATE TABLE NodeLocation
(
    i     INTEGER PRIMARY KEY REFERENCES Node (i),
    world TEXT CHECK ( world IS NULL OR world IN ('New', 'Old', 'Space') ),
    x     INTEGER,
    y     INTEGER,
    CHECK ( (x IS NULL AND y IS NULL) OR (x IS NOT NULL AND y IS NOT NULL) )
) STRICT;
CREATE TABLE NodeLocationSource
(
    i           INTEGER NOT NULL REFERENCES NodeLocation (i),
    source      INTEGER NOT NULL REFERENCES Source (priority),
    world       INTEGER NOT NULL CHECK ( world IN (0, 1) ),
    coordinates INTEGER NOT NULL CHECK ( coordinates IN (0, 1) ),
    PRIMARY KEY (i, source)
) STRICT;


CREATE TABLE AirAirline
(
    i    INTEGER PRIMARY KEY REFERENCES Node (i),
    name TEXT NOT NULL,
    link TEXT
) STRICT;
CREATE TABLE AirAirlineSource
(
    i      INTEGER NOT NULL REFERENCES AirAirline (i),
    source INTEGER NOT NULL REFERENCES Source (priority),
    link   INTEGER NOT NULL CHECK ( link IN (0, 1) ),
    PRIMARY KEY (i, source)
) STRICT;

CREATE TABLE AirAirport
(
    i    INTEGER PRIMARY KEY REFERENCES NodeLocation (i),
    code TEXT NOT NULL,
    link TEXT
) STRICT;
CREATE TABLE AirAirportNames
(
    i    INTEGER NOT NULL REFERENCES AirAirport (i),
    name TEXT    NOT NULL,
    UNIQUE (i, name)
) STRICT;
CREATE TABLE AirAirportModes
(
    i    INTEGER NOT NULL REFERENCES AirAirport (i),
    mode TEXT    NOT NULL CHECK ( mode IN ('helicopter', 'seaplane', 'warp plane', 'traincarts plane') ),
    UNIQUE (i, mode)
) STRICT;
CREATE TABLE AirAirportSource
(
    i      INTEGER NOT NULL REFERENCES AirAirport (i),
    source INTEGER NOT NULL REFERENCES Source (priority),
    names  INTEGER NOT NULL CHECK ( names IN (0, 1) ),
    link   INTEGER NOT NULL CHECK ( link IN (0, 1) ),
    modes  INTEGER NOT NULL CHECK ( modes IN (0, 1) ),
    PRIMARY KEY (i, source)
) STRICT;

CREATE TABLE AirFlight
(
    i       INTEGER PRIMARY KEY REFERENCES Node (i),
    "from"  INTEGER NOT NULL REFERENCES AirGate (i),
    "to"    INTEGER NOT NULL REFERENCES AirGate (i),
    code    TEXT    NOT NULL,
    mode    TEXT CHECK ( mode IS NULL OR mode IN ('helicopter', 'seaplane', 'warp plane', 'traincarts plane') ),
    airline INTEGER NOT NULL REFERENCES AirAirline (i)
) STRICT;
CREATE TABLE AirFlightSource
(
    i      INTEGER NOT NULL REFERENCES AirFlight (i),
    source INTEGER NOT NULL REFERENCES Source (priority),
    mode   INTEGER NOT NULL CHECK ( mode IN (0, 1) ),
    PRIMARY KEY (i, source)
) STRICT;

CREATE TABLE AirGate
(
    i       INTEGER PRIMARY KEY REFERENCES Node (i),
    code    TEXT,
    airport INTEGER NOT NULL REFERENCES AirAirport (i),
    airline INTEGER REFERENCES AirAirline (i),
    size    TEXT,
    mode    TEXT CHECK ( mode IS NULL OR mode IN ('helicopter', 'seaplane', 'warp plane', 'traincarts plane') )
) STRICT;
CREATE TABLE AirGateSource
(
    i       INTEGER NOT NULL REFERENCES AirGate (i),
    source  INTEGER NOT NULL REFERENCES Source (priority),
    size    INTEGER NOT NULL CHECK ( size IN (0, 1) ),
    mode    INTEGER NOT NULL CHECK ( mode IN (0, 1) ),
    airline INTEGER NOT NULL CHECK ( airline IN (0, 1) ),
    PRIMARY KEY (i, source)
) STRICT;


CREATE TABLE BusCompany
(
    i    INTEGER PRIMARY KEY REFERENCES Node (i),
    name TEXT NOT NULL
) STRICT;
CREATE TABLE BusCompanySource
(
    i      INTEGER NOT NULL REFERENCES BusCompany (i),
    source INTEGER NOT NULL REFERENCES Source (priority),
    PRIMARY KEY (i, source)
) STRICT;

CREATE TABLE BusLine
(
    i       INTEGER PRIMARY KEY REFERENCES Node (i),
    code    TEXT    NOT NULL,
    company INTEGER NOT NULL REFERENCES BusCompany (i),
    name    TEXT,
    colour  TEXT,
    mode    TEXT CHECK ( mode IS NULL OR mode IN ('warp', 'traincarts') ),
    local   INTEGER CHECK ( local IS NULL OR local IN (0, 1) )
) STRICT;
CREATE TABLE BusLineSource
(
    i      INTEGER NOT NULL REFERENCES BusLine (i),
    source INTEGER NOT NULL REFERENCES Source (priority),
    name   INTEGER NOT NULL CHECK ( name IN (0, 1) ),
    colour INTEGER NOT NULL CHECK ( colour IN (0, 1) ),
    mode   INTEGER NOT NULL CHECK ( mode IN (0, 1) ),
    local  INTEGER NOT NULL CHECK ( local IN (0, 1) ),
    PRIMARY KEY (i, source)
) STRICT;

CREATE TABLE BusStop
(
    i       INTEGER PRIMARY KEY REFERENCES NodeLocation (i),
    name    TEXT,
    company INTEGER NOT NULL REFERENCES BusCompany (i)
) STRICT;
CREATE TABLE BusStopCodes
(
    i    INTEGER NOT NULL REFERENCES BusStop (i),
    code TEXT    NOT NULL,
    UNIQUE (i, code)
) STRICT;
CREATE TABLE BusStopSource
(
    i      INTEGER NOT NULL REFERENCES BusLine (i),
    source INTEGER NOT NULL REFERENCES Source (priority),
    name   INTEGER NOT NULL CHECK ( name IN (0, 1) ),
    PRIMARY KEY (i, source)
) STRICT;

CREATE TABLE BusBerth
(
    i    INTEGER PRIMARY KEY REFERENCES Node (i),
    code TEXT,
    stop INTEGER NOT NULL REFERENCES BusStop

) STRICT;
CREATE TABLE BusBerthSource
(
    i      INTEGER NOT NULL REFERENCES BusBerth (i),
    source INTEGER NOT NULL REFERENCES Source (priority),
    PRIMARY KEY (i, source)
) STRICT;

CREATE TABLE BusConnection
(
    i         INTEGER PRIMARY KEY REFERENCES Node (i),
    line      INTEGER NOT NULL REFERENCES BusLine (i),
    "from"    INTEGER NOT NULL REFERENCES BusBerth (i),
    "to"      INTEGER NOT NULL REFERENCES BusBerth (i),
    direction TEXT
) STRICT;
CREATE TABLE BusConnectionSource
(
    i         INTEGER NOT NULL REFERENCES BusLine (i),
    source    INTEGER NOT NULL REFERENCES Source (priority),
    direction INTEGER NOT NULL CHECK ( direction IN (0, 1) ),
    PRIMARY KEY (i, source)
) STRICT;


CREATE TABLE SeaCompany
(
    i    INTEGER PRIMARY KEY REFERENCES Node (i),
    name TEXT NOT NULL
) STRICT;
CREATE TABLE SeaCompanySource
(
    i      INTEGER NOT NULL REFERENCES SeaCompany (i),
    source INTEGER NOT NULL REFERENCES Source (priority),
    PRIMARY KEY (i, source)
) STRICT;

CREATE TABLE SeaLine
(
    i       INTEGER PRIMARY KEY REFERENCES Node (i),
    code    TEXT    NOT NULL,
    company INTEGER NOT NULL REFERENCES SeaCompany (i),
    name    TEXT,
    colour  TEXT,
    mode    TEXT CHECK ( mode IS NULL OR mode IN ('cruise', 'warp ferry', 'traincarts ferry') ),
    local   INTEGER CHECK ( local IS NULL OR local IN (0, 1) )
) STRICT;
CREATE TABLE SeaLineSource
(
    i      INTEGER NOT NULL REFERENCES SeaLine (i),
    source INTEGER NOT NULL REFERENCES Source (priority),
    name   INTEGER NOT NULL CHECK ( name IN (0, 1) ),
    colour INTEGER NOT NULL CHECK ( colour IN (0, 1) ),
    mode   INTEGER NOT NULL CHECK ( mode IN (0, 1) ),
    local  INTEGER NOT NULL CHECK ( local IN (0, 1) ),
    PRIMARY KEY (i, source)
) STRICT;

CREATE TABLE SeaStop
(
    i       INTEGER PRIMARY KEY REFERENCES NodeLocation (i),
    name    TEXT,
    company INTEGER NOT NULL REFERENCES SeaCompany (i)
) STRICT;
CREATE TABLE SeaStopCodes
(
    i    INTEGER NOT NULL REFERENCES SeaStop (i),
    code TEXT    NOT NULL,
    UNIQUE (i, code)
) STRICT;
CREATE TABLE SeaStopSource
(
    i      INTEGER NOT NULL REFERENCES SeaLine (i),
    source INTEGER NOT NULL REFERENCES Source (priority),
    name   INTEGER NOT NULL CHECK ( name IN (0, 1) ),
    PRIMARY KEY (i, source)
) STRICT;

CREATE TABLE SeaDock
(
    i    INTEGER PRIMARY KEY REFERENCES Node (i),
    code TEXT,
    stop INTEGER NOT NULL REFERENCES SeaStop

) STRICT;
CREATE TABLE SeaDockSource
(
    i      INTEGER NOT NULL REFERENCES SeaDock (i),
    source INTEGER NOT NULL REFERENCES Source (priority),
    PRIMARY KEY (i, source)
) STRICT;

CREATE TABLE SeaConnection
(
    i         INTEGER PRIMARY KEY REFERENCES Node (i),
    line      INTEGER NOT NULL REFERENCES SeaLine (i),
    "from"    INTEGER NOT NULL REFERENCES SeaDock (i),
    "to"      INTEGER NOT NULL REFERENCES SeaDock (i),
    direction TEXT
) STRICT;
CREATE TABLE SeaConnectionSource
(
    i         INTEGER NOT NULL REFERENCES SeaLine (i),
    source    INTEGER NOT NULL REFERENCES Source (priority),
    direction INTEGER NOT NULL CHECK ( direction IN (0, 1) ),
    PRIMARY KEY (i, source)
) STRICT;


CREATE TABLE RailCompany
(
    i    INTEGER PRIMARY KEY REFERENCES Node (i),
    name TEXT NOT NULL
) STRICT;
CREATE TABLE RailCompanySource
(
    i      INTEGER NOT NULL REFERENCES RailCompany (i),
    source INTEGER NOT NULL REFERENCES Source (priority),
    PRIMARY KEY (i, source)
) STRICT;

CREATE TABLE RailLine
(
    i       INTEGER PRIMARY KEY REFERENCES Node (i),
    code    TEXT    NOT NULL,
    company INTEGER NOT NULL REFERENCES RailCompany (i),
    name    TEXT,
    colour  TEXT,
    mode    TEXT CHECK ( mode IS NULL OR mode IN ('warp', 'cart', 'traincarts', 'vehicles') ),
    local   INTEGER CHECK ( local IS NULL OR local IN (0, 1) )
) STRICT;
CREATE TABLE RailLineSource
(
    i      INTEGER NOT NULL REFERENCES RailLine (i),
    source INTEGER NOT NULL REFERENCES Source (priority),
    name   INTEGER NOT NULL CHECK ( name IN (0, 1) ),
    colour INTEGER NOT NULL CHECK ( colour IN (0, 1) ),
    mode   INTEGER NOT NULL CHECK ( mode IN (0, 1) ),
    local  INTEGER NOT NULL CHECK ( local IN (0, 1) ),
    PRIMARY KEY (i, source)
) STRICT;

CREATE TABLE RailStation
(
    i       INTEGER PRIMARY KEY REFERENCES NodeLocation (i),
    name    TEXT,
    company INTEGER NOT NULL REFERENCES RailCompany (i)
) STRICT;
CREATE TABLE RailStationCodes
(
    i    INTEGER NOT NULL REFERENCES RailStation (i),
    code TEXT    NOT NULL,
    UNIQUE (i, code)
) STRICT;
CREATE TABLE RailStationSource
(
    i      INTEGER NOT NULL REFERENCES RailLine (i),
    source INTEGER NOT NULL REFERENCES Source (priority),
    name   INTEGER NOT NULL CHECK ( name IN (0, 1) ),
    PRIMARY KEY (i, source)
) STRICT;

CREATE TABLE RailPlatform
(
    i       INTEGER PRIMARY KEY REFERENCES Node (i),
    code    TEXT,
    station INTEGER NOT NULL REFERENCES RailStation

) STRICT;
CREATE TABLE RailPlatformSource
(
    i      INTEGER NOT NULL REFERENCES RailPlatform (i),
    source INTEGER NOT NULL REFERENCES Source (priority),
    PRIMARY KEY (i, source)
) STRICT;

CREATE TABLE RailConnection
(
    i         INTEGER PRIMARY KEY REFERENCES Node (i),
    line      INTEGER NOT NULL REFERENCES RailLine (i),
    "from"    INTEGER NOT NULL REFERENCES RailPlatform (i),
    "to"      INTEGER NOT NULL REFERENCES RailPlatform (i),
    direction TEXT
) STRICT;
CREATE TABLE RailConnectionSource
(
    i         INTEGER NOT NULL REFERENCES RailLine (i),
    source    INTEGER NOT NULL REFERENCES Source (priority),
    direction INTEGER NOT NULL CHECK ( direction IN (0, 1) ),
    PRIMARY KEY (i, source)
) STRICT;


CREATE TABLE SpawnWarp
(
    i        INTEGER PRIMARY KEY REFERENCES NodeLocation (i),
    name     TEXT NOT NULL,
    warpType TEXT NOT NULL
) STRICT;

CREATE TABLE Town
(
    i           INTEGER PRIMARY KEY REFERENCES NodeLocation (i),
    name        TEXT NOT NULL,
    rank        TEXT NOT NULL CHECK ( rank IN
                                      ('Unranked', 'Councillor', 'Mayor', 'Senator', 'Governor', 'Premier', 'Community') ),
    mayor       TEXT NOT NULL,
    deputyMayor TEXT
) STRICT;


CREATE TABLE Proximity
(
    node1    INTEGER NOT NULL REFERENCES NodeLocation (i),
    node2    INTEGER NOT NULL REFERENCES NodeLocation (i),
    distance REAL    NOT NULL,
    explicit INTEGER NOT NULL CHECK ( explicit IN (0, 1) ),
    PRIMARY KEY (node1, node2),
    CHECK ( node1 < node2 )
) STRICT;
CREATE TABLE ProximitySource
(
    node1  INTEGER NOT NULL REFERENCES NodeLocation (i),
    node2  INTEGER NOT NULL REFERENCES NodeLocation (i),
    source INTEGER NOT NULL REFERENCES Source (priority),
    PRIMARY KEY (node1, node2, source),
    FOREIGN KEY (node1, node2) REFERENCES Proximity (node1, node2)
) STRICT;

CREATE TABLE SharedFacility
(
    node1 INTEGER NOT NULL REFERENCES NodeLocation (i),
    node2 INTEGER NOT NULL REFERENCES NodeLocation (i),
    PRIMARY KEY (node1, node2),
    CHECK ( node1 < node2 )
) STRICT;

COMMIT;