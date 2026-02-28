import datetime
from collections.abc import Iterator
from typing import ClassVar, TypedDict
from uuid import UUID

import msgspec

from gatelogue_aggregator.config import Config
from gatelogue_aggregator.downloader import get_url
from gatelogue_aggregator.logging import INFO1, progress_bar


class Warp(msgspec.Struct):
    id: int
    name: str
    player_uuid: UUID = msgspec.field(name="playerUUID")
    world_uuid: UUID = msgspec.field(name="worldUUID")
    x: float
    y: float
    z: float
    pitch: float
    yaw: float
    creation_date: datetime.datetime = msgspec.field(name="creationDate")
    type: int
    visits: int
    welcome_message: str = msgspec.field(name="welcomeMessage")

    @property
    def coordinates(self) -> tuple[int, int]:
        return round(self.x), round(self.z)


class WarpAPI:
    warps: ClassVar[list[Warp]] = []

    LINK: ClassVar[str] = "https://api.minecartrapidtransit.net/api/v2/warps"

    @classmethod
    def prepare(cls, config: Config):
        if len(cls.warps) != 0:
            return

        with progress_bar(INFO1, "Downloading warps from MRT Warp API"):
            offset = 0
            while True:
                ls = msgspec.json.decode(
                    get_url(cls.LINK + f"?offset={offset}", "mrt-api/" + str(offset), config),
                    type=TypedDict("", {"pagination": dict, "result": list[Warp]}),
                )["result"]
                if len(ls) == 0:
                    break
                cls.warps.extend(ls)
                offset += len(ls)

    @classmethod
    def from_user(cls, uuid: str | UUID) -> Iterator[Warp]:
        uuid = UUID(uuid) if isinstance(uuid, str) else uuid
        return (a for a in cls.warps if a.player_uuid == uuid)
