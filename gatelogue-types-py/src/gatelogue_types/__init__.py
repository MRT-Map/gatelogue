from __future__ import annotations

import contextlib
import datetime
import urllib.request
from typing import TYPE_CHECKING, Generic, Literal, Self, TypeVar

import msgspec

from gatelogue_types.__about__ import __version__

if TYPE_CHECKING:
    from collections.abc import Iterator

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
    AirAirline.NS()
    | AirAirport.NS()
    | AirFlight.NS()
    | AirGate.NS()
    | BusCompany.NS()
    | BusLine.NS()
    | BusStop.NS()
    | SeaCompany.NS()
    | SeaLine.NS()
    | SeaStop.NS()
    | RailCompany.NS()
    | RailLine.NS()
    | RailStation.NS()
    | SpawnWarp.NS()
    | Town.NS()
)


class GatelogueData(msgspec.Struct, kw_only=True):
    nodes: dict[ID, Nodes]
    """List of all nodes, along with their connections to other nodes"""
    timestamp: str = msgspec.field(default_factory=lambda: datetime.datetime.now().isoformat())  # noqa: DTZ005
    """Time that the aggregation of the data was done"""
    version: int = int(__version__.split("+")[1])
    """Version number of the database format"""

    @classmethod
    def NS(cls):  # noqa: N802
        class NS(cls, kw_only=True, tag=cls.__name__):
            nodes: dict[ID, NodesNS]

            @classmethod
            def get(cls, *args, **kwargs) -> Self:
                return cls._get(
                    "https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data_no_sources.json",
                    cls.NS(),
                    *args,
                    **kwargs,
                )

            @classmethod
            async def aiohttp_get(cls, session: aiohttp.ClientSession | None = None) -> Self:
                return cls._aiohttp_get(
                    "https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data_no_sources.json",
                    cls.NS(),
                    session,
                )

        NS.__name__ = cls.__name__
        return NS

    @classmethod
    def get(cls, *args, **kwargs) -> Self:
        return cls._get(
            "https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data.json", cls, *args, **kwargs
        )

    @classmethod
    async def aiohttp_get(cls, session: aiohttp.ClientSession | None = None) -> Self:
        return cls._aiohttp_get(
            "https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data.json", cls, session
        )

    @classmethod
    def _get(cls, url: str, ty: type[msgspec.Struct], *args, **kwargs):
        with contextlib.suppress(ImportError):
            import niquests

            return msgspec.json.decode(niquests.get(url, *args, **kwargs).text, type=ty)
        with contextlib.suppress(ImportError):
            import requests

            return msgspec.json.decode(requests.get(url, *args, **kwargs).text, type=ty)  # noqa: S113
        with contextlib.suppress(ImportError):
            import httpx

            return msgspec.json.decode(httpx.get(url, *args, **kwargs).text, type=ty)
        with contextlib.suppress(ImportError):
            import urllib3

            return msgspec.json.decode(urllib3.request("GET", url, *args, **kwargs).data, type=ty)
        if not url.startswith("https:"):
            raise ValueError
        with urllib.request.urlopen(url, *args, **kwargs) as response:  # noqa: S310
            return msgspec.json.decode(response.read(), type=ty)

    @classmethod
    async def _aiohttp_get(cls, url: str, ty: type[msgspec.Struct], session: aiohttp.ClientSession | None = None):
        import aiohttp

        session = aiohttp.ClientSession() if session is None else contextlib.nullcontext(session)
        async with session as session, session.get(url) as response:
            return msgspec.json.decode(await response.text(), type=ty)

    def __iter__(self) -> Iterator[Node]:
        return iter(self.nodes.values())

    def __getitem__(self, item: ID) -> Node:
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


class Node(msgspec.Struct, kw_only=True, tag=True):
    i: ID = None
    source: set[str] = msgspec.field(default_factory=set)

    @classmethod
    def NS(cls):  # noqa: N802
        class NS(cls, kw_only=True, tag=cls.__name__):
            pass

        NS.__name__ = cls.__name__
        return NS

    def __str__(self) -> str:
        return (
            type(self).__name__
            + "("
            + ",".join(f"{k}={v}" for k, v in msgspec.structs.asdict(self).items() if v is not None)
            + ")"
        )


class LocatedNode(Node, kw_only=True, tag=True):
    coordinates: Sourced[tuple[float, float]] | None = None
    """Coordinates of the object"""
    world: Sourced[World] | None = None
    """Whether the object is in the New or Old world"""

    proximity: dict[ID, Sourced[Proximity]] = msgspec.field(default_factory=dict)
    """
    References all objects that are near (within walking distance of) this object.
    It is represented as an inner mapping of object IDs to proximity data (:py:class:`Proximity`).
    For example, ``{1234: <proximity>}`` means that there is an object with ID ``1234`` near this object, and ``<proximity>`` is a :py:class:`Proximity` object.
    """
    shared_facility: list[Sourced[ID]] = msgspec.field(default_factory=list)
    """References all objects that this object shares the same facility with (same building, station, hub etc)"""

    @classmethod
    def NS(cls):  # noqa: N802
        class NS(cls, kw_only=True, tag=cls.__name__):
            coordinates: tuple[float, float] | None = None
            world: World | None = None
            proximity: dict[ID, Proximity] = msgspec.field(default_factory=dict)
            shared_facility: list[ID] = msgspec.field(default_factory=list)

        NS.__name__ = cls.__name__
        return NS


class AirFlight(Node, kw_only=True, tag=True):
    codes: set[str]
    """Unique flight code(s). **2-letter airline prefix not included**"""
    mode: Sourced[PlaneMode] | None = None
    """Type of air vehicle or technology used on the flight"""

    gates: list[Sourced[ID]] = msgspec.field(default_factory=list)
    """List of IDs of :py:class:`AirGate` s that the flight goes to. Should be of length 2 in most cases"""
    airline: Sourced[ID] = None
    """ID of the :py:class:`AirAirline` the flight is operated by"""

    @classmethod
    def NS(cls):  # noqa: N802
        class NS(cls, Node.NS(), kw_only=True, tag=cls.__name__):
            mode: PlaneMode | None = None
            gates: list[ID] = msgspec.field(default_factory=list)
            airline: ID

        NS.__name__ = cls.__name__
        return NS


class AirAirport(LocatedNode, kw_only=True, tag=True):
    code: str
    """Unique 3 (sometimes 4)-letter code"""
    name: Sourced[str] | None = None
    """Name of the airport"""
    link: Sourced[str] | None = None
    """Link to the MRT Wiki page for the airport"""
    modes: Sourced[set[PlaneMode]] | None = None
    """Modes offered by the airport"""

    gates: list[Sourced[ID]] = msgspec.field(default_factory=list)
    """List of IDs of :py:class:`AirGate` s"""

    @classmethod
    def NS(cls):  # noqa: N802
        class NS(cls, LocatedNode.NS(), kw_only=True, tag=cls.__name__):
            name: str | None = None
            link: str | None = None
            modes: set[PlaneMode] | None = None
            gates: list[ID] = msgspec.field(default_factory=list)

        NS.__name__ = cls.__name__
        return NS


class AirGate(Node, kw_only=True, tag=True):
    code: str | None
    """Unique gate code. If ``None``, all flights under this gate do not have gate information at this airport"""
    size: Sourced[str] | None = None
    """Abbreviated size of the gate (eg. ``S``, ``M``)"""

    flights: list[Sourced[ID]] = msgspec.field(default_factory=list)
    """List of IDs of :py:class:`AirFlight` s that stop at this gate. If ``code==None``, all flights under this gate do not have gate information at this airport"""
    airport: Sourced[ID] = None
    """ID of the :py:class:`AirAirport`"""
    airline: Sourced[ID] | None = None
    """ID of the :py:class:`AirAirline` that owns the gate"""

    @classmethod
    def NS(cls):  # noqa: N802
        class NS(cls, Node.NS(), kw_only=True, tag=cls.__name__):
            size: str | None = None
            flights: list[ID] = msgspec.field(default_factory=list)
            airport: ID
            airline: ID | None = None

        NS.__name__ = cls.__name__
        return NS


class AirAirline(Node, kw_only=True, tag=True):
    name: str
    """Name of the airline"""
    link: Sourced[str] | None = None
    """Link to the MRT Wiki page for the airline"""

    flights: list[Sourced[ID]] = msgspec.field(default_factory=list)
    """List of IDs of all :py:class:`AirFlight` s the airline operates"""
    gates: list[Sourced[ID]] = msgspec.field(default_factory=list)
    """List of IDs of all :py:class:`AirGate` s the airline owns or operates"""

    @classmethod
    def NS(cls):  # noqa: N802
        class NS(cls, Node.NS(), kw_only=True, tag=cls.__name__):
            link: str | None = None
            flights: list[ID] = msgspec.field(default_factory=list)
            gates: list[ID] = msgspec.field(default_factory=list)

        NS.__name__ = cls.__name__
        return NS


type PlaneMode = Literal["helicopter", "seaplane", "warp plane", "traincarts plane"]


class RailCompany(Node, kw_only=True, tag=True):
    name: str
    """Name of the Rail company"""

    lines: list[Sourced[ID]] = msgspec.field(default_factory=list)
    """List of IDs of all :py:class:`RailLine` s the company operates"""
    stations: list[Sourced[ID]] = msgspec.field(default_factory=list)
    """List of all :py:class:`RailStation` s the company's lines stop at"""
    local: bool = False
    """Whether the company operates within the city, e.g. a metro system"""

    @classmethod
    def NS(cls):  # noqa: N802
        class NS(cls, Node.NS(), kw_only=True, tag=cls.__name__):
            lines: list[ID] = msgspec.field(default_factory=list)
            stations: list[ID] = msgspec.field(default_factory=list)

        NS.__name__ = cls.__name__
        return NS


class RailLine(Node, kw_only=True, tag=True):
    code: str
    """Unique code identifying the Rail line"""
    name: Sourced[str] | None = None
    """Name of the line"""
    colour: Sourced[str] | None = None
    """Colour of the line (on a map)"""
    mode: Sourced[RailMode] | None = None
    """Type of rail or rail technology used on the line"""

    company: Sourced[ID] = None
    """ID of the :py:class:`RailCompany` that operates the line"""
    ref_station: Sourced[ID] | None = None
    """ID of one :py:class:`RailStation` on the line, typically a terminus"""

    @classmethod
    def NS(cls):  # noqa: N802
        class NS(cls, Node.NS(), kw_only=True, tag=cls.__name__):
            name: str | None = None
            colour: str | None = None
            mode: RailMode | None = None
            company: ID = None
            ref_station: ID | None = None

        NS.__name__ = cls.__name__
        return NS


class RailStation(LocatedNode, kw_only=True, tag=True):
    codes: set[str]
    """Unique code(s) identifying the Rail station. May also be the same as the name"""
    name: Sourced[str] | None = None
    """Name of the station"""

    company: Sourced[ID] = None
    """ID of the :py:class:`RailCompany` that stops here"""
    connections: dict[ID, list[Sourced[Connection]]] = msgspec.field(default_factory=dict)
    """
    References all next stations on the lines serving this station.
    It is represented as a mapping of station IDs to a list of connection data (:py:class:`RailConnection`), each encoding line and route information.
    For example, ``{1234: [<conn1>, <conn2>]}`` means that the station with ID ``1234`` is the next station from here on two lines.
    """

    @classmethod
    def NS(cls):  # noqa: N802
        class NS(cls, LocatedNode.NS(), kw_only=True, tag=cls.__name__):
            name: str | None = None
            company: ID = None
            connections: dict[ID, list[Connection.NS()]] = msgspec.field(default_factory=dict)

        NS.__name__ = cls.__name__
        return NS


type RailMode = Literal["warp", "cart", "traincarts", "vehicles"]


class BusCompany(Node, kw_only=True, tag=True):
    name: str
    """Name of the bus company"""

    lines: list[Sourced[ID]] = msgspec.field(default_factory=list)
    """List of IDs of all :py:class:`BusLine` s the company operates"""
    stops: list[Sourced[ID]] = msgspec.field(default_factory=list)
    """List of all :py:class:`BusStop` s the company's lines stop at"""
    local: bool = False
    """Whether the company operates within the city, e.g. a city bus network"""

    @classmethod
    def NS(cls):  # noqa: N802
        class NS(cls, Node.NS(), Node.NS(), kw_only=True, tag=cls.__name__):
            lines: list[ID] = msgspec.field(default_factory=list)
            stops: list[ID] = msgspec.field(default_factory=list)

        NS.__name__ = cls.__name__
        return NS


class BusLine(Node, kw_only=True, tag=True):
    code: str
    """Unique code identifying the bus line"""
    name: Sourced[str] | None = None
    """Name of the line"""
    colour: Sourced[str] | None = None
    """Colour of the line (on a map)"""

    company: Sourced[ID] = None
    """ID of the :py:class:`BusCompany` that operates the line"""
    ref_stop: Sourced[ID] | None = None
    """ID of one :py:class:`BusStop` on the line, typically a terminus"""

    @classmethod
    def NS(cls):  # noqa: N802
        class NS(cls, kw_only=True, tag=cls.__name__):
            name: str | None = None
            colour: str | None = None
            company: ID = None
            ref_stop: ID | None = None

        NS.__name__ = cls.__name__
        return NS


class BusStop(LocatedNode, kw_only=True, tag=True):
    codes: set[str]
    """Unique code(s) identifying the bus stop. May also be the same as the name"""
    name: Sourced[str] | None = None
    """Name of the stop"""

    company: Sourced[ID] = None
    """ID of the :py:class:`BusCompany` that stops here"""
    connections: dict[ID, list[Sourced[Connection]]] = msgspec.field(default_factory=dict)
    """
    References all next stops on the lines serving this stop.
    It is represented as a mapping of stop IDs to a list of connection data (:py:class:`BusConnection`), each encoding line and route information.
    For example, ``{1234: [<conn1>, <conn2>]}`` means that the stop with ID ``1234`` is the next stop from here on two lines.
    """

    @classmethod
    def NS(cls):  # noqa: N802
        class NS(cls, LocatedNode.NS(), kw_only=True, tag=cls.__name__):
            name: str | None = None
            company: ID = None
            connections: dict[ID, list[Connection.NS()]] = msgspec.field(default_factory=dict)

        NS.__name__ = cls.__name__
        return NS


class SeaCompany(Node, kw_only=True, tag=True):
    name: str
    """Name of the Sea company"""

    lines: list[Sourced[ID]] = msgspec.field(default_factory=list)
    """List of IDs of all :py:class:`SeaLine` s the company operates"""
    stops: list[Sourced[ID]] = msgspec.field(default_factory=list)
    """List of all :py:class:`SeaStop` s the company's lines stop at"""
    local: bool = False
    """Whether the company operates within the city, e.g. a local ferry line"""

    @classmethod
    def NS(cls):  # noqa: N802
        class NS(cls, Node.NS(), kw_only=True, tag=cls.__name__):
            lines: list[ID] = msgspec.field(default_factory=list)
            stops: list[ID] = msgspec.field(default_factory=list)

        NS.__name__ = cls.__name__
        return NS


class SeaLine(Node, kw_only=True, tag=True):
    code: str
    """Unique code identifying the Sea line"""
    name: Sourced[str] | None = None
    """Name of the line"""
    colour: Sourced[str] | None = None
    """Colour of the line (on a map)"""
    mode: Sourced[SeaMode] | None = None
    """Type of boat used on the line"""

    company: Sourced[ID] = None
    """ID of the :py:class:`SeaCompany` that operates the line"""
    ref_stop: Sourced[ID] | None = None
    """ID of one :py:class:`SeaStop` on the line, typically a terminus"""

    @classmethod
    def NS(cls):  # noqa: N802
        class NS(cls, Node.NS(), kw_only=True, tag=cls.__name__):
            name: str | None = None
            colour: str | None = None
            mode: SeaMode | None = None
            company: ID = None
            ref_stop: ID | None = None

        NS.__name__ = cls.__name__
        return NS


class SeaStop(LocatedNode, kw_only=True, tag=True):
    codes: set[str]
    """Unique code(s) identifying the Sea stop. May also be the same as the name"""
    name: Sourced[str] | None = None
    """Name of the stop"""

    company: Sourced[ID] = None
    """ID of the :py:class:`SeaCompany` that stops here"""
    connections: dict[ID, list[Sourced[Connection]]] = msgspec.field(default_factory=dict)
    """
    References all next stops on the lines serving this stop.
    It is represented as a mapping of stop IDs to a list of connection data (:py:class:`SeaConnection`), each encoding line and route information.
    For example, ``{1234: [<conn1>, <conn2>]}`` means that the stop with ID ``1234`` is the next stop from here on two lines.
    """

    @classmethod
    def NS(cls):  # noqa: N802
        class NS(cls, LocatedNode.NS(), kw_only=True, tag=cls.__name__):
            name: str | None = None
            company: ID = None
            connections: dict[ID, list[Connection.NS()]] = msgspec.field(default_factory=dict)

        NS.__name__ = cls.__name__
        return NS


type SeaMode = Literal["ferry", "cruise"]


class SpawnWarp(LocatedNode, kw_only=True, tag=True):
    name: str
    """Name of the spawn warp"""
    warp_type: WarpType
    """The type of warp"""

    @classmethod
    def NS(cls):  # noqa: N802
        class NS(cls, LocatedNode.NS(), kw_only=True, tag=cls.__name__):
            pass

        NS.__name__ = cls.__name__
        return NS


type WarpType = Literal["premier", "terminus", "portal", "misc"]


class Town(LocatedNode, kw_only=True, tag=True):
    name: str
    """Name of the town"""
    rank: Sourced[Rank]
    """Rank of the town"""
    mayor: Sourced[str]
    """Mayor of the town"""
    deputy_mayor: Sourced[str | None]
    """Deputy Mayor of the town"""

    @classmethod
    def NS(cls):  # noqa: N802
        class NS(cls, LocatedNode.NS(), kw_only=True, tag=cls.__name__):
            rank: Rank
            mayor: str
            deputy_mayor: str | None

        NS.__name__ = cls.__name__
        return NS


type Rank = Literal["Unranked", "Councillor", "Mayor", "Senator", "Governor", "Premier", "Community"]


class Connection(msgspec.Struct):
    line: ID
    """Reference to or ID of the line that the connection is made on"""
    direction: Direction | None = None
    """Direction information"""

    @classmethod
    def NS(cls):  # noqa: N802
        class NS(cls, kw_only=True, tag=cls.__name__):
            direction: Direction.NS() | None = None

        NS.__name__ = cls.__name__
        return NS


class Direction(msgspec.Struct):
    direction: ID
    """Reference to or ID of the station/stop that the other fields take with respect to. Should be either node of the connection"""
    forward_label: str | None
    """Describes the direction taken when travelling **towards the station/stop in** ``forward_towards_code``"""
    backward_label: str | None
    """Describes the direction taken when travelling **from the station/stop in** ``forward_towards_code``"""
    one_way: bool | Sourced[bool] = False
    """Whether the connection is one-way, ie. travel **towards the station/stop in** ``forward_towards_code`` is possible but not the other way"""

    @classmethod
    def NS(cls):  # noqa: N802
        class NS(cls, kw_only=True, tag=cls.__name__):
            one_way: bool = False

        NS.__name__ = cls.__name__
        return NS
