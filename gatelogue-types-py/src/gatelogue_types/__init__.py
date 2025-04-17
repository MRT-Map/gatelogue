from __future__ import annotations

import contextlib
import datetime
import urllib.request
from typing import TYPE_CHECKING, Literal, Self, Generic, TypeVar

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


class GatelogueData(msgspec.Struct, kw_only=True):
    nodes: dict[ID, Nodes]
    """List of all nodes, along with their connections to other nodes"""
    timestamp: str = msgspec.field(default_factory=lambda: datetime.datetime.now().isoformat())  # noqa: DTZ005
    """Time that the aggregation of the data was done"""
    version: int = int(__version__.split("+")[1])
    """Version number of the database format"""

    def __iter__(self) -> Iterator[Nodes]:
        return iter(self.nodes.values())

    def __getitem__(self, item: ID) -> Nodes:
        return self.nodes[item]

    @classmethod
    def get_with_sources(cls, *args, **kwargs) -> Self:
        return cls._get(
            "https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data.json", *args, **kwargs
        )

    @classmethod
    def get_no_sources(cls, *args, **kwargs) -> Self:
        return cls._get(
            "https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data_no_sources.json", *args, **kwargs
        )

    @classmethod
    def _get(cls, url: str, *args, **kwargs) -> Self:
        with contextlib.suppress(ImportError):
            import niquests

            return msgspec.json.decode(niquests.get(url, *args, **kwargs).text, type=cls)
        with contextlib.suppress(ImportError):
            import requests

            return msgspec.json.decode(requests.get(url, *args, **kwargs).text, type=cls)  # noqa: S113
        with contextlib.suppress(ImportError):
            import httpx

            return msgspec.json.decode(httpx.get(url, *args, **kwargs).text, type=cls)
        if not url.startswith("https:"):
            raise ValueError
        with urllib.request.urlopen(url, *args, **kwargs) as response:  # noqa: S310
            return msgspec.json.decode(response.read(), type=cls)

    @classmethod
    async def aiohttp_get_with_sources(cls, session: aiohttp.ClientSession | None = None) -> Self:
        return cls._aiohttp_get(
            "https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data.json", session
        )

    @classmethod
    async def aiohttp_get_no_sources(cls, session: aiohttp.ClientSession | None = None) -> Self:
        return cls._aiohttp_get(
            "https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data_no_sources.json", session
        )

    @classmethod
    async def _aiohttp_get(cls, url: str, session: aiohttp.ClientSession | None = None):
        import aiohttp

        session = aiohttp.ClientSession() if session is None else contextlib.nullcontext(session)
        async with session as session, session.get(url) as response:
            return msgspec.json.decode(await response.text(), type=cls)


T = TypeVar("T")

class Sourced_(msgspec.Struct, Generic[T]):  # noqa: N801
    v: T
    """Actual value"""
    s: set[str] = msgspec.field(default_factory=set)
    """List of sources that support the value"""

    def __str__(self):
        s = str(self.v)
        if len(self.s) != 0:
            s += " (" + ", ".join(str(a) for a in self.s) + ")"
        return s

type Sourced[T] = Sourced_[T]

type World = Literal["New", "Old", "Space"]


class Proximity(msgspec.Struct):
    distance: float
    """Distance between the two objects in blocks"""
    explicit: bool = False
    """Whether this relation is explicitly recognised by the company/ies of the stations. Used mostly for local services"""


class Node(msgspec.Struct, kw_only=True, tag=True):
    i: ID = None
    source: set[str] = msgspec.field(default_factory=set)

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

    proximity: dict[ID, Sourced[Proximity]] = None
    """
    References all objects that are near (within walking distance of) this object.
    It is represented as an inner mapping of object IDs to proximity data (:py:class:`Proximity`).
    For example, ``{1234: <proximity>}`` means that there is an object with ID ``1234`` near this object, and ``<proximity>`` is a :py:class:`Proximity` object.
    """
    shared_facility: list[Sourced[ID]] = None
    """References all objects that this object shares the same facility with (same building, station, hub etc)"""


class AirFlight(Node, kw_only=True, tag=True):
    codes: set[str]
    """Unique flight code(s). **2-letter airline prefix not included**"""
    mode: Sourced[PlaneMode] | None = None
    """Type of air vehicle or technology used on the flight"""

    # noinspection PyDataclass
    gates: list[Sourced[ID]] = None
    """List of IDs of :py:class:`AirGate` s that the flight goes to. Should be of length 2 in most cases"""
    airline: Sourced[ID] = None
    """ID of the :py:class:`AirAirline` the flight is operated by"""


class AirAirport(LocatedNode, kw_only=True, tag=True):
    code: str
    """Unique 3 (sometimes 4)-letter code"""
    name: Sourced[str] | None = None
    """Name of the airport"""
    link: Sourced[str] | None = None
    """Link to the MRT Wiki page for the airport"""
    modes: Sourced[set[PlaneMode]] | None = None
    """Modes offered by the airport"""

    gates: list[Sourced[ID]] = None
    """List of IDs of :py:class:`AirGate` s"""


class AirGate(Node, kw_only=True, tag=True):
    code: str | None
    """Unique gate code. If ``None``, all flights under this gate do not have gate information at this airport"""
    size: Sourced[str] | None = None
    """Abbreviated size of the gate (eg. ``S``, ``M``)"""

    flights: list[Sourced[ID]] = None
    """List of IDs of :py:class:`AirFlight` s that stop at this gate. If ``code==None``, all flights under this gate do not have gate information at this airport"""
    airport: Sourced[ID] = None
    """ID of the :py:class:`AirAirport`"""
    airline: Sourced[ID] | None = None
    """ID of the :py:class:`AirAirline` that owns the gate"""


class AirAirline(Node, kw_only=True, tag=True):
    name: str
    """Name of the airline"""
    link: Sourced[str] | None = None
    """Link to the MRT Wiki page for the airline"""

    flights: list[Sourced[ID]] | None = None
    """List of IDs of all :py:class:`AirFlight` s the airline operates"""
    gates: list[Sourced[ID]] | None = None
    """List of IDs of all :py:class:`AirGate` s the airline owns or operates"""


type PlaneMode = Literal["helicopter", "seaplane", "warp plane", "traincarts plane"]


class RailCompany(Node, kw_only=True, tag=True):
    name: str
    """Name of the Rail company"""

    lines: list[Sourced[ID]] = None
    """List of IDs of all :py:class:`RailLine` s the company operates"""
    stations: list[Sourced[ID]] = None
    """List of all :py:class:`RailStation` s the company's lines stop at"""
    local: bool = False
    """Whether the company operates within the city, e.g. a metro system"""


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


class RailStation(LocatedNode, kw_only=True, tag=True):
    codes: set[str]
    """Unique code(s) identifying the Rail station. May also be the same as the name"""
    name: Sourced[str] | None = None
    """Name of the station"""

    company: Sourced[ID] = None
    """ID of the :py:class:`RailCompany` that stops here"""
    connections: dict[ID, list[Sourced[Connection]]] = None
    """
    References all next stations on the lines serving this station.
    It is represented as a mapping of station IDs to a list of connection data (:py:class:`RailConnection`), each encoding line and route information.
    For example, ``{1234: [<conn1>, <conn2>]}`` means that the station with ID ``1234`` is the next station from here on two lines.
    """


type RailMode = Literal["warp", "cart", "traincarts", "vehicles"]


class BusCompany(Node, kw_only=True, tag=True):
    name: str
    """Name of the bus company"""

    lines: list[Sourced[ID]] = None
    """List of IDs of all :py:class:`BusLine` s the company operates"""
    stops: list[Sourced[ID]] = None
    """List of all :py:class:`BusStop` s the company's lines stop at"""
    local: bool = False
    """Whether the company operates within the city, e.g. a city bus network"""


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


class BusStop(LocatedNode, kw_only=True, tag=True):
    codes: set[str]
    """Unique code(s) identifying the bus stop. May also be the same as the name"""
    name: Sourced[str] | None = None
    """Name of the stop"""

    company: Sourced[ID] = None
    """ID of the :py:class:`BusCompany` that stops here"""
    connections: dict[ID, list[Sourced[Connection]]] = None
    """
    References all next stops on the lines serving this stop.
    It is represented as a mapping of stop IDs to a list of connection data (:py:class:`BusConnection`), each encoding line and route information.
    For example, ``{1234: [<conn1>, <conn2>]}`` means that the stop with ID ``1234`` is the next stop from here on two lines.
    """


class SeaCompany(Node, kw_only=True, tag=True):
    name: str
    """Name of the Sea company"""

    lines: list[Sourced[ID]] = None
    """List of IDs of all :py:class:`SeaLine` s the company operates"""
    stops: list[Sourced[ID]] = None
    """List of all :py:class:`SeaStop` s the company's lines stop at"""
    local: bool = False
    """Whether the company operates within the city, e.g. a local ferry line"""


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


class SeaStop(LocatedNode, kw_only=True, tag=True):
    codes: set[str]
    """Unique code(s) identifying the Sea stop. May also be the same as the name"""
    name: Sourced[str] | None = None
    """Name of the stop"""

    company: Sourced[ID] = None
    """ID of the :py:class:`SeaCompany` that stops here"""
    connections: dict[ID, list[Sourced[Connection]]] = None
    """
    References all next stops on the lines serving this stop.
    It is represented as a mapping of stop IDs to a list of connection data (:py:class:`SeaConnection`), each encoding line and route information.
    For example, ``{1234: [<conn1>, <conn2>]}`` means that the stop with ID ``1234`` is the next stop from here on two lines.
    """


type SeaMode = Literal["ferry", "cruise"]


class SpawnWarp(LocatedNode, kw_only=True, tag=True):
    name: str
    """Name of the spawn warp"""
    warp_type: WarpType
    """The type of warp"""


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


type Rank = Literal["Unranked", "Councillor", "Mayor", "Senator", "Governor", "Premier", "Community"]


class Connection(msgspec.Struct):
    line: ID
    """Reference to or ID of the line that the connection is made on"""
    direction: Direction | None = None
    """Direction information"""


class Direction(msgspec.Struct):
    direction: ID
    """Reference to or ID of the station/stop that the other fields take with respect to. Should be either node of the connection"""
    forward_label: str | None
    """Describes the direction taken when travelling **towards the station/stop in** ``forward_towards_code``"""
    backward_label: str | None
    """Describes the direction taken when travelling **from the station/stop in** ``forward_towards_code``"""
    one_way: bool | Sourced[bool] = False
    """Whether the connection is one-way, ie. travel **towards the station/stop in** ``forward_towards_code`` is possible but not the other way"""
