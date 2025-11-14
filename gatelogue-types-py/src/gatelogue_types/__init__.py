from __future__ import annotations

import contextlib
import datetime
import urllib.request
from typing import TYPE_CHECKING, Any, Generic, Literal, Self, TypeVar

import msgspec

from gatelogue_types.__about__ import __data_version__

if TYPE_CHECKING:
    from collections.abc import Iterator

    # pyrefly: ignore [missing-import]
    import aiohttp

type ID = int

type Nodes = (
    AirAirline
    | AirAirport
    | AirFlight
    | AirGate
    | BusCompany
    | BusLine
    | BusStop
    | SeaCompany
    | SeaLine
    | SeaStop
    | RailCompany
    | RailLine
    | RailStation
    | SpawnWarp
    | Town
)
type NodesNS = (
    AirAirlineNS
    | AirAirportNS
    | AirFlightNS
    | AirGateNS
    | BusCompanyNS
    | BusLineNS
    | BusStopNS
    | SeaCompanyNS
    | SeaLineNS
    | SeaStopNS
    | RailCompanyNS
    | RailLineNS
    | RailStationNS
    | SpawnWarpNS
    | TownNS
)


class _GatelogueData(msgspec.Struct, kw_only=True):
    nodes: Any
    """List of all nodes, along with their connections to other nodes"""
    timestamp: str = msgspec.field(default_factory=lambda: datetime.datetime.now().isoformat())  # noqa: DTZ005
    """Time that the aggregation of the data was done"""
    version: int = __data_version__
    """Version number of the database format"""

    @classmethod
    def _get(cls, url: str, *args, **kwargs) -> Self:
        with contextlib.suppress(ImportError):
            # pyrefly: ignore [missing-import]
            import niquests

            return msgspec.json.decode(niquests.get(url, *args, **kwargs).text, type=cls)
        with contextlib.suppress(ImportError):
            # pyrefly: ignore [missing-source-for-stubs]
            import requests

            return msgspec.json.decode(requests.get(url, *args, **kwargs).text, type=cls)  # noqa: S113
        with contextlib.suppress(ImportError):
            # pyrefly: ignore [missing-import]
            import httpx

            return msgspec.json.decode(httpx.get(url, *args, **kwargs).text, type=cls)
        with contextlib.suppress(ImportError):
            # pyrefly: ignore [missing-import]
            import urllib3

            return msgspec.json.decode(urllib3.request("GET", url, *args, **kwargs).data, type=cls)
        if not url.startswith("https:"):
            raise ValueError
        with urllib.request.urlopen(url, *args, **kwargs) as response:  # noqa: S310
            return msgspec.json.decode(response.read(), type=cls)

    @classmethod
    async def _aiohttp_get(cls, url: str, session: aiohttp.ClientSession | None = None) -> Self:
        # pyrefly: ignore [missing-import]
        import aiohttp

        session = aiohttp.ClientSession() if session is None else contextlib.nullcontext(session)
        async with session as session, session.get(url) as response:  # pyrefly: ignore [missing-attribute]
            return msgspec.json.decode(await response.text(), type=cls)


class GatelogueData(_GatelogueData, tag=_GatelogueData.__name__.removeprefix("_")):
    nodes: dict[ID, Nodes]

    @classmethod
    def get(cls, *args, **kwargs) -> Self:
        return cls._get(
            "https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data.json", *args, **kwargs
        )

    @classmethod
    async def aiohttp_get(cls, session: aiohttp.ClientSession | None = None) -> Self:
        return await cls._aiohttp_get(
            "https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data.json", session
        )

    def __iter__(self) -> Iterator[Nodes]:
        return iter(self.nodes.values())

    def __getitem__(self, item: ID) -> Nodes:
        return self.nodes[item]


class GatelogueDataNS(_GatelogueData, tag=GatelogueData.__name__.removeprefix("_")):
    nodes: dict[ID, NodesNS]

    @classmethod
    def get(cls, *args, **kwargs) -> Self:
        return cls._get(
            "https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data_no_sources.json",
            *args,
            **kwargs,
        )

    @classmethod
    async def aiohttp_get(cls, session: aiohttp.ClientSession | None = None) -> Self:
        return await cls._aiohttp_get(
            "https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data_no_sources.json",
            session,
        )

    def __iter__(self) -> Iterator[NodesNS]:
        return iter(self.nodes.values())

    def __getitem__(self, item: ID) -> NodesNS:
        return self.nodes[item]


T = TypeVar("T")


class Sourced(msgspec.Struct, Generic[T]):
    v: T
    """Actual value"""
    s: set[str] = msgspec.field(default_factory=set)
    """List of sources that support the value"""

    def __str__(self):
        s = str(self.v)
        if len(self.s) != 0:
            s += " (" + ", ".join(str(a) for a in self.s) + ")"
        return s


type World = Literal["New", "Old", "Space"]


class Proximity(msgspec.Struct):
    distance: float
    """Distance between the two objects in blocks"""
    explicit: bool = False
    """Whether this relation is explicitly recognised by the company/ies of the stations. Used mostly for local services"""


class _Node(msgspec.Struct, kw_only=True, tag=True):
    # pyrefly: ignore [bad-assignment]
    i: ID = None
    """The ID of the node"""
    source: set[str] = msgspec.field(default_factory=set)
    """All sources that prove the node's existence"""

    def __str__(self) -> str:
        return (
            type(self).__name__.removeprefix("_")
            + "("
            + ",".join(f"{k}={v}" for k, v in msgspec.structs.asdict(self).items() if v is not None)
            + ")"
        )


class Node(_Node, tag=_Node.__name__.removeprefix("_")):
    pass


class NodeNS(_Node, tag=_Node.__name__.removeprefix("_")):
    pass


class _LocatedNode(_Node, kw_only=True, tag=True):
    coordinates: Any
    """Coordinates of the object"""
    world: Any
    """Whether the object is in the New or Old world"""

    proximity: Any
    """
    References all objects that are near (within walking distance of) this object.
    It is represented as an inner mapping of object IDs to proximity data (:py:class:`Proximity`).
    For example, ``{1234: <proximity>}`` means that there is an object with ID ``1234`` near this object, and ``<proximity>`` is a :py:class:`Proximity` object.
    """
    shared_facility: Any
    """References all objects that this object shares the same facility with (same building, station, hub etc)"""


class LocatedNode(Node, _LocatedNode, tag=_LocatedNode.__name__.removeprefix("_")):
    coordinates: Sourced[tuple[float, float]] | None = None
    world: Sourced[World] | None = None

    proximity: dict[ID, Sourced[Proximity]] = msgspec.field(default_factory=dict)
    shared_facility: list[Sourced[ID]] = msgspec.field(default_factory=list)


class LocatedNodeNS(NodeNS, _LocatedNode, tag=_LocatedNode.__name__.removeprefix("_")):
    coordinates: tuple[float, float] | None = None
    world: World | None = None

    proximity: dict[ID, Proximity] = msgspec.field(default_factory=dict)
    shared_facility: list[ID] = msgspec.field(default_factory=list)


class _AirFlight(_Node, kw_only=True, tag=True):
    codes: set[str]
    """Unique flight code(s). **2-letter airline prefix not included**"""
    mode: Any
    """Type of air vehicle or technology used on the flight"""

    gates: Any
    """List of IDs of :py:class:`AirGate` s that the flight goes to. Should be of length 2 in most cases"""
    airline: Any
    """ID of the :py:class:`AirAirline` the flight is operated by"""


class AirFlight(Node, _AirFlight, kw_only=True, tag=_AirFlight.__name__.removeprefix("_")):
    mode: Sourced[PlaneMode] | None = None

    gates: list[Sourced[ID]] = msgspec.field(default_factory=list)
    # pyrefly: ignore [bad-assignment]
    airline: Sourced[ID] = None


class AirFlightNS(NodeNS, _AirFlight, kw_only=True, tag=_AirFlight.__name__.removeprefix("_")):
    mode: PlaneMode | None = None

    gates: list[ID] = msgspec.field(default_factory=list)
    airline: ID


class _AirAirport(_LocatedNode, kw_only=True, tag=True):
    code: str
    """Unique 3 (sometimes 4)-letter code"""
    names: Any
    """Name(s) of the airport"""
    link: Any
    """Link to the MRT Wiki page for the airport"""
    modes: Any
    """Modes offered by the airport"""

    gates: Any
    """List of IDs of :py:class:`AirGate` s"""


class AirAirport(LocatedNode, _AirAirport, kw_only=True, tag=_AirAirport.__name__.removeprefix("_")):
    names: Sourced[set[str]] | None = None
    link: Sourced[str] | None = None
    modes: Sourced[set[PlaneMode]] | None = None

    gates: list[Sourced[ID]] = msgspec.field(default_factory=list)


class AirAirportNS(LocatedNodeNS, _AirAirport, kw_only=True, tag=_AirAirport.__name__.removeprefix("_")):
    names: set[str] | None = None
    link: str | None = None
    modes: set[PlaneMode] | None = None

    gates: list[ID] = msgspec.field(default_factory=list)


class _AirGate(_Node, kw_only=True, tag=True):
    code: str | None
    """Unique gate code. If ``None``, all flights under this gate do not have gate information at this airport"""
    size: Any
    """Abbreviated size of the gate (eg. ``S``, ``M``)"""

    flights: Any
    """List of IDs of :py:class:`AirFlight` s that stop at this gate. If ``code==None``, all flights under this gate do not have gate information at this airport"""
    airport: Any
    """ID of the :py:class:`AirAirport`"""
    airline: Any
    """ID of the :py:class:`AirAirline` that owns the gate"""


class AirGate(Node, _AirGate, kw_only=True, tag=_AirGate.__name__.removeprefix("_")):
    size: Sourced[str] | None = None

    flights: list[Sourced[ID]] = msgspec.field(default_factory=list)
    # pyrefly: ignore [bad-assignment]
    airport: Sourced[ID] = None
    airline: Sourced[ID] | None = None


class AirGateNS(NodeNS, _AirGate, kw_only=True, tag=_AirGate.__name__.removeprefix("_")):
    size: str | None = None

    flights: list[ID] = msgspec.field(default_factory=list)
    airport: ID
    airline: ID | None = None


class _AirAirline(_Node, kw_only=True, tag=True):
    name: str
    """Name of the airline"""
    link: Any
    """Link to the MRT Wiki page for the airline"""

    flights: Any
    """List of IDs of all :py:class:`AirFlight` s the airline operates"""
    gates: Any
    """List of IDs of all :py:class:`AirGate` s the airline owns or operates"""


class AirAirline(Node, _AirAirline, kw_only=True, tag=_AirAirline.__name__.removeprefix("_")):
    link: Sourced[str] | None = None

    flights: list[Sourced[ID]] = msgspec.field(default_factory=list)
    gates: list[Sourced[ID]] = msgspec.field(default_factory=list)


class AirAirlineNS(NodeNS, _AirAirline, kw_only=True, tag=_AirAirline.__name__.removeprefix("_")):
    link: str | None = None

    flights: list[ID] = msgspec.field(default_factory=list)
    gates: list[ID] = msgspec.field(default_factory=list)


type PlaneMode = Literal["helicopter", "seaplane", "warp plane", "traincarts plane"]


class _RailCompany(_Node, kw_only=True, tag=True):
    name: str
    """Name of the Rail company"""

    lines: Any
    """List of IDs of all :py:class:`RailLine` s the company operates"""
    stations: Any
    """List of all :py:class:`RailStation` s the company's lines stop at"""
    local: bool = False
    """Whether the company operates within the city, e.g. a metro system"""


class RailCompany(Node, _RailCompany, kw_only=True, tag=_RailCompany.__name__.removeprefix("_")):
    lines: list[Sourced[ID]] = msgspec.field(default_factory=list)
    stations: list[Sourced[ID]] = msgspec.field(default_factory=list)


class RailCompanyNS(NodeNS, _RailCompany, kw_only=True, tag=_RailCompany.__name__.removeprefix("_")):
    lines: list[ID] = msgspec.field(default_factory=list)
    stations: list[ID] = msgspec.field(default_factory=list)


class _RailLine(_Node, kw_only=True, tag=True):
    code: str
    """Unique code identifying the Rail line"""
    name: Any
    """Name of the line"""
    colour: Any
    """Colour of the line (on a map)"""
    mode: Any
    """Type of rail or rail technology used on the line"""

    company: Any
    """ID of the :py:class:`RailCompany` that operates the line"""
    stations: Any
    """List of all :py:class:`RailStation` s the line stops at"""


class RailLine(Node, _RailLine, kw_only=True, tag=_RailLine.__name__.removeprefix("_")):
    name: Sourced[str] | None = None
    colour: Sourced[str] | None = None
    mode: Sourced[RailMode] | None = None

    # pyrefly: ignore [bad-assignment]
    company: Sourced[ID] = None
    stations: list[Sourced[ID]] = msgspec.field(default_factory=list)


class RailLineNS(NodeNS, _RailLine, kw_only=True, tag=_RailLine.__name__.removeprefix("_")):
    name: str | None = None
    colour: str | None = None
    mode: RailMode | None = None

    # pyrefly: ignore [bad-assignment]
    company: ID = None
    stations: list[ID] = msgspec.field(default_factory=list)


class _RailStation(_LocatedNode, kw_only=True, tag=True):
    codes: set[str]
    """Unique code(s) identifying the Rail station. May also be the same as the name"""
    name: Any
    """Name of the station"""

    company: Any
    """ID of the :py:class:`RailCompany` that stops here"""
    connections: Any
    """
    References all next stations on the lines serving this station.
    It is represented as a mapping of station IDs to a list of connection data (:py:class:`RailConnection`), each encoding line and route information.
    For example, ``{1234: [<conn1>, <conn2>]}`` means that the station with ID ``1234`` is the next station from here on two lines.
    """


class RailStation(LocatedNode, _RailStation, kw_only=True, tag=_RailStation.__name__.removeprefix("_")):
    name: Sourced[str] | None = None

    # pyrefly: ignore [bad-assignment]
    company: Sourced[ID] = None
    connections: dict[ID, list[Sourced[Connection]]] = msgspec.field(default_factory=dict)


class RailStationNS(LocatedNodeNS, _RailStation, kw_only=True, tag=_RailStation.__name__.removeprefix("_")):
    name: str | None = None

    # pyrefly: ignore [bad-assignment]
    company: ID = None
    connections: dict[ID, list[ConnectionNS]] = msgspec.field(default_factory=dict)


type RailMode = Literal["warp", "cart", "traincarts", "vehicles"]


class _BusCompany(_Node, kw_only=True, tag=True):
    name: str
    """Name of the bus company"""

    lines: Any
    """List of IDs of all :py:class:`BusLine` s the company operates"""
    stops: Any
    """List of all :py:class:`BusStop` s the company's lines stop at"""
    local: bool = False
    """Whether the company operates within the city, e.g. a city bus network"""


class BusCompany(Node, _BusCompany, kw_only=True, tag=_BusCompany.__name__.removeprefix("_")):
    lines: list[Sourced[ID]] = msgspec.field(default_factory=list)
    stops: list[Sourced[ID]] = msgspec.field(default_factory=list)


class BusCompanyNS(NodeNS, _BusCompany, kw_only=True, tag=_BusCompany.__name__.removeprefix("_")):
    lines: list[ID] = msgspec.field(default_factory=list)
    stops: list[ID] = msgspec.field(default_factory=list)


class _BusLine(_Node, kw_only=True, tag=True):
    code: str
    """Unique code identifying the bus line"""
    name: Any
    """Name of the line"""
    colour: Any
    """Colour of the line (on a map)"""

    company: Any
    """ID of the :py:class:`BusCompany` that operates the line"""
    stops: Any
    """List of all :py:class:`BusStop` s the line stops at"""


class BusLine(Node, _BusLine, kw_only=True, tag=_BusLine.__name__.removeprefix("_")):
    name: Sourced[str] | None = None
    colour: Sourced[str] | None = None

    # pyrefly: ignore [bad-assignment]
    company: Sourced[ID] = None
    stops: list[Sourced[ID]] = msgspec.field(default_factory=list)


class BusLineNS(NodeNS, _BusLine, kw_only=True, tag=_BusLine.__name__.removeprefix("_")):
    name: str | None = None
    colour: str | None = None

    # pyrefly: ignore [bad-assignment]
    company: ID = None
    stops: list[ID] = msgspec.field(default_factory=list)


class _BusStop(_LocatedNode, kw_only=True, tag=True):
    codes: set[str]
    """Unique code(s) identifying the bus stop. May also be the same as the name"""
    name: Any
    """Name of the stop"""

    company: Any
    """ID of the :py:class:`BusCompany` that stops here"""
    connections: Any
    """
    References all next stops on the lines serving this stop.
    It is represented as a mapping of stop IDs to a list of connection data (:py:class:`BusConnection`), each encoding line and route information.
    For example, ``{1234: [<conn1>, <conn2>]}`` means that the stop with ID ``1234`` is the next stop from here on two lines.
    """


class BusStop(LocatedNode, _BusStop, kw_only=True, tag=_BusStop.__name__.removeprefix("_")):
    name: Sourced[str] | None = None

    # pyrefly: ignore [bad-assignment]
    company: Sourced[ID] = None
    connections: dict[ID, list[Sourced[Connection]]] = msgspec.field(default_factory=dict)


class BusStopNS(LocatedNodeNS, _BusStop, kw_only=True, tag=_BusStop.__name__.removeprefix("_")):
    name: str | None = None

    # pyrefly: ignore [bad-assignment]
    company: ID = None
    connections: dict[ID, list[ConnectionNS]] = msgspec.field(default_factory=dict)


class _SeaCompany(_Node, kw_only=True, tag=True):
    name: str
    """Name of the Sea company"""

    lines: Any
    """List of IDs of all :py:class:`SeaLine` s the company operates"""
    stops: Any
    """List of all :py:class:`SeaStop` s the company's lines stop at"""
    local: bool = False
    """Whether the company operates within the city, e.g. a local ferry line"""


class SeaCompany(Node, _SeaCompany, kw_only=True, tag=_SeaCompany.__name__.removeprefix("_")):
    lines: list[Sourced[ID]] = msgspec.field(default_factory=list)
    stops: list[Sourced[ID]] = msgspec.field(default_factory=list)


class SeaCompanyNS(NodeNS, _SeaCompany, kw_only=True, tag=_SeaCompany.__name__.removeprefix("_")):
    lines: list[ID] = msgspec.field(default_factory=list)
    stops: list[ID] = msgspec.field(default_factory=list)


class _SeaLine(_Node, kw_only=True, tag=True):
    code: str
    """Unique code identifying the Sea line"""
    name: Any
    """Name of the line"""
    colour: Any
    """Colour of the line (on a map)"""
    mode: Any
    """Type of boat used on the line"""

    company: Any
    """ID of the :py:class:`SeaCompany` that operates the line"""
    stops: Any
    """List of all :py:class:`SeaStop` s the line stops at"""


class SeaLine(Node, _SeaLine, kw_only=True, tag=_SeaLine.__name__.removeprefix("_")):
    name: Sourced[str] | None = None
    colour: Sourced[str] | None = None
    mode: Sourced[SeaMode] | None = None

    # pyrefly: ignore [bad-assignment]
    company: Sourced[ID] = None
    stops: list[Sourced[ID]] = msgspec.field(default_factory=list)


class SeaLineNS(NodeNS, _SeaLine, kw_only=True, tag=_SeaLine.__name__.removeprefix("_")):
    name: str | None = None
    colour: str | None = None
    mode: SeaMode | None = None

    # pyrefly: ignore [bad-assignment]
    company: ID = None
    stops: list[ID] = msgspec.field(default_factory=list)


class _SeaStop(_LocatedNode, kw_only=True, tag=True):
    codes: set[str]
    """Unique code(s) identifying the Sea stop. May also be the same as the name"""
    name: Any
    """Name of the stop"""

    company: Any
    """ID of the :py:class:`SeaCompany` that stops here"""
    connections: Any
    """
    References all next stops on the lines serving this stop.
    It is represented as a mapping of stop IDs to a list of connection data (:py:class:`SeaConnection`), each encoding line and route information.
    For example, ``{1234: [<conn1>, <conn2>]}`` means that the stop with ID ``1234`` is the next stop from here on two lines.
    """


class SeaStop(LocatedNode, _SeaStop, kw_only=True, tag=_SeaStop.__name__.removeprefix("_")):
    name: Sourced[str] | None = None

    # pyrefly: ignore [bad-assignment]
    company: Sourced[ID] = None
    connections: dict[ID, list[Sourced[Connection]]] = msgspec.field(default_factory=dict)


class SeaStopNS(LocatedNodeNS, _SeaStop, kw_only=True, tag=_SeaStop.__name__.removeprefix("_")):
    name: str | None = None

    # pyrefly: ignore [bad-assignment]
    company: ID = None
    connections: dict[ID, list[ConnectionNS]] = msgspec.field(default_factory=dict)


type SeaMode = Literal["ferry", "cruise"]


class _SpawnWarp(_LocatedNode, kw_only=True, tag=True):
    name: str
    """Name of the spawn warp"""
    warp_type: WarpType
    """The type of warp"""


class SpawnWarp(LocatedNode, _SpawnWarp, kw_only=True, tag=_SpawnWarp.__name__.removeprefix("_")):
    pass


class SpawnWarpNS(LocatedNodeNS, _SpawnWarp, kw_only=True, tag=_SpawnWarp.__name__.removeprefix("_")):
    pass


type WarpType = Literal["premier", "terminus", "portal", "misc"]


class _Town(_LocatedNode, kw_only=True, tag=True):
    name: str
    """Name of the town"""
    rank: Any
    """Rank of the town"""
    mayor: Any
    """Mayor of the town"""
    deputy_mayor: Any
    """Deputy Mayor of the town"""


class Town(LocatedNode, _Town, kw_only=True, tag=_Town.__name__.removeprefix("_")):
    rank: Sourced[Rank]
    mayor: Sourced[str]
    deputy_mayor: Sourced[str | None]


class TownNS(LocatedNodeNS, _Town, kw_only=True, tag=_Town.__name__.removeprefix("_")):
    rank: Rank
    mayor: str
    deputy_mayor: str | None


type Rank = Literal["Unranked", "Councillor", "Mayor", "Senator", "Governor", "Premier", "Community"]


class _Connection(msgspec.Struct):
    line: ID
    """Reference to or ID of the line that the connection is made on"""
    direction: Any
    """Direction information"""


class Connection(_Connection, kw_only=True, tag=_Connection.__name__.removeprefix("_")):
    direction: Direction | None = None


class ConnectionNS(_Connection, kw_only=True, tag=_Connection.__name__.removeprefix("_")):
    direction: DirectionNS | None = None


class _Direction(msgspec.Struct):
    direction: ID
    """Reference to or ID of the station/stop that the other fields take with respect to. Should be either node of the connection"""
    forward_label: str | None
    """Describes the direction taken when travelling **towards the station/stop in** ``forward_towards_code``"""
    backward_label: str | None
    """Describes the direction taken when travelling **from the station/stop in** ``forward_towards_code``"""
    one_way: Any
    """Whether the connection is one-way, ie. travel **towards the station/stop in** ``forward_towards_code`` is possible but not the other way"""


class Direction(_Direction, kw_only=True, tag=_Direction.__name__.removeprefix("_")):
    one_way: bool | Sourced[bool] = False


class DirectionNS(_Direction, kw_only=True, tag=_Direction.__name__.removeprefix("_")):
    one_way: bool = False
