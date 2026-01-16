"""Dev-only demo data generators.

Provides dependency clients that generate lots of deterministic mock flights.
Enabled via env in the API lifespan (see specs/001-dev_demo_data_mode.md).

No PII is generated or logged.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from datetime import datetime, timedelta

from flybot.clients import EmptiesClient, EmptiesSnapshot, Flight, ScheduleClient


def _stable_int_hash(text: str) -> int:
    digest = hashlib.md5(text.encode("utf-8"), usedforsecurity=False).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


@dataclass(frozen=True)
class DemoConfig:
    seed: int = 0
    outbound_count: int = 200
    return_count: int = 400


class DemoEmptiesClient(EmptiesClient):
    """Generates outbound flights on demand for the requested route."""

    def __init__(self, config: DemoConfig):
        self._config = config

    async def get_empties(
        self,
        origin: str,
        destination: str,
        lookahead_minutes: int,
        snapshot_time: datetime,
    ) -> EmptiesSnapshot | None:
        route_seed = self._config.seed ^ _stable_int_hash(f"empties:{origin}:{destination}")
        rng = random.Random(route_seed)

        flights: list[Flight] = []
        max_minutes = max(1, int(lookahead_minutes))

        for i in range(self._config.outbound_count):
            depart_offset_min = rng.randint(0, max_minutes)
            departure = snapshot_time + timedelta(minutes=depart_offset_min)
            arrival = departure + timedelta(minutes=rng.randint(120, 260))

            capacity = rng.randint(110, 220)
            open_seats = rng.randint(0, 35)

            # Keep all flights route-consistent.
            flight_number = f"AS{1000 + i}"
            flights.append(
                Flight(
                    flight_number=flight_number,
                    origin=origin,
                    destination=destination,
                    departure=departure,
                    arrival=arrival,
                    open_seats=open_seats,
                    capacity=capacity,
                )
            )

        return EmptiesSnapshot(snapshot_time=snapshot_time, flights=flights, is_stale=False)


class DemoScheduleClient(ScheduleClient):
    """Generates return flights on demand within the requested window."""

    def __init__(self, config: DemoConfig):
        self._config = config

    async def get_return_flights(
        self,
        origin: str,
        destination: str,
        earliest: datetime,
        latest: datetime,
    ) -> list[Flight] | None:
        route_seed = self._config.seed ^ _stable_int_hash(f"schedule:{origin}:{destination}")
        rng = random.Random(route_seed)

        # Ensure sane window.
        if latest <= earliest:
            return []

        total_minutes = int((latest - earliest).total_seconds() // 60)
        total_minutes = max(1, total_minutes)

        flights: list[Flight] = []

        for i in range(self._config.return_count):
            depart_offset_min = rng.randint(0, total_minutes)
            departure = earliest + timedelta(minutes=depart_offset_min)
            arrival = departure + timedelta(minutes=rng.randint(120, 260))

            capacity = rng.randint(110, 220)
            flight_number = f"AS{5000 + i}"

            flights.append(
                Flight(
                    flight_number=flight_number,
                    origin=origin,
                    destination=destination,
                    departure=departure,
                    arrival=arrival,
                    capacity=capacity,
                )
            )

        return flights


def make_demo_clients(
    *,
    seed: int = 0,
    outbound_count: int = 200,
    return_count: int = 400,
) -> tuple[EmptiesClient, ScheduleClient]:
    config = DemoConfig(seed=seed, outbound_count=outbound_count, return_count=return_count)
    return DemoEmptiesClient(config), DemoScheduleClient(config)
