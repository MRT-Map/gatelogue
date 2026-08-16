import datetime
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from math import ceil
from typing import ClassVar
from uuid import UUID

import gatelogue_types as gt
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

    @property
    def world(self) -> gt.World | None:
        return (
            "New"
            if self.world_uuid == UUID("253ced62-9637-4f7b-a32d-4e3e8e767bd1")
            else "Old"
            if self.world_uuid == UUID("59e29aa1-7e98-4d40-bac7-594905b734a9")
            else None
        )


class Pagination(msgspec.Struct):
    limit: int
    offset: int
    hits: int
    total_hits: int


class WarpAPIResult(msgspec.Struct):
    pagination: Pagination
    result: list[Warp]


class WarpAPI:
    warps: ClassVar[list[Warp]] = []

    LINK: ClassVar[str] = "https://api.minecartrapidtransit.net/api/v2/warps"

    @classmethod
    def prepare(cls, config: Config):
        if len(cls.warps) != 0:
            return

        with progress_bar(INFO1, "Downloading warps from MRT Warp API"):
            init_result = msgspec.json.decode(get_url(cls.LINK, "mrt-api/0", config), type=WarpAPIResult)
            cls.warps.extend(init_result.result)
            with ThreadPoolExecutor(max_workers=ceil(config.max_workers / 4)) as executor:
                for result in executor.map(
                    lambda offset: msgspec.json.decode(
                        get_url(cls.LINK + f"?offset={offset}", "mrt-api/" + str(offset), config), type=WarpAPIResult
                    ),
                    range(
                        init_result.pagination.limit, init_result.pagination.total_hits, init_result.pagination.limit
                    ),
                ):
                    cls.warps.extend(result.result)

    @classmethod
    def from_user(cls, uuid: str | UUID) -> Iterator[Warp]:
        uuid = UUID(uuid) if isinstance(uuid, str) else uuid
        return (a for a in cls.warps if a.player_uuid == uuid)
