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


def _estimate_flight_duration(origin: str, destination: str, rng: random.Random) -> int:
    """Estimate realistic flight duration in minutes based on city pairs."""
    # Rough distance categories (in reality would use actual great circle distance)
    route_key = tuple(sorted([origin, destination]))
    
    # Short haul: < 500 miles (SEA-PDX, LAX-SFO, etc.)
    short_haul = [("PDX", "SEA"), ("LAX", "SFO"), ("SAN", "LAX")]
    # Medium haul: 500-1500 miles (SEA-LAX, PDX-SFO, etc.)
    medium_haul = [("PDX", "SFO"), ("SEA", "LAX"), ("SEA", "SAN")]
    # Long haul: > 1500 miles (SEA-JFK, LAX-JFK, etc.)
    
    if route_key in short_haul:
        # 1-2 hours
        base = 75
        variance = 25
    elif route_key in medium_haul:
        # 2-3 hours
        base = 150
        variance = 30
    else:
        # 3-5 hours (assume medium-long haul)
        base = 240
        variance = 60
    
    return base + rng.randint(-variance, variance)


def _get_aircraft_capacity(rng: random.Random) -> tuple[int, str]:
    """Return realistic aircraft capacity and type."""
    # Alaska Airlines common aircraft types
    aircraft_types = [
        (76, "737-700", 0.25),   # Smaller aircraft
        (124, "737-800", 0.30),  # Common workhorse
        (178, "737-900ER", 0.25),# Larger single aisle
        (157, "737 MAX 9", 0.20), # Newer aircraft
    ]
    
    # Weighted random selection
    total_weight = sum(w for _, _, w in aircraft_types)
    pick = rng.random() * total_weight
    
    cumulative = 0.0
    for capacity, aircraft, weight in aircraft_types:
        cumulative += weight
        if pick <= cumulative:
            # Add some variance to exact capacity
            actual_capacity = capacity + rng.randint(-3, 3)
            return max(50, actual_capacity), aircraft
    
    return 124, "737-800"


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
            # More flights during peak hours (6-9am, 4-7pm)
            # Use weighted distribution for departure times
            hour_of_day = snapshot_time.hour + (snapshot_time.minute / 60.0)
            
            # Prefer peak hours: early morning (6-9) and evening (16-19)
            if rng.random() < 0.6:  # 60% of flights during peaks
                if rng.random() < 0.5:
                    # Morning peak
                    target_hour = rng.uniform(6.0, 9.0)
                else:
                    # Evening peak
                    target_hour = rng.uniform(16.0, 19.0)
                
                # Calculate offset to target hour
                hours_offset = target_hour - hour_of_day
                if hours_offset < 0:
                    hours_offset += 24  # Next day
                depart_offset_min = int(hours_offset * 60) + rng.randint(-30, 30)
                depart_offset_min = max(0, min(max_minutes, depart_offset_min))
            else:
                # Off-peak: uniform distribution
                depart_offset_min = rng.randint(0, max_minutes)
            
            departure = snapshot_time + timedelta(minutes=depart_offset_min)
            
            # Realistic flight duration based on route
            flight_duration = _estimate_flight_duration(origin, destination, rng)
            arrival = departure + timedelta(minutes=flight_duration)

            # Realistic aircraft capacity and type
            capacity, aircraft_type = _get_aircraft_capacity(rng)
            
            # More realistic open seat distribution:
            # Most flights are 70-95% full, with occasional empty or completely full flights
            load_factor = rng.betavariate(7, 2)  # Skewed toward high load factors
            occupied = int(capacity * load_factor)
            open_seats = max(0, capacity - occupied)
            
            # Flight numbers vary by time of day (lower numbers = earlier flights)
            hour = departure.hour
            base_flight_num = 1000 + (hour * 50) + (i % 50)
            flight_number = f"AS{base_flight_num}"
            
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
            # More flights during peak return hours (late afternoon/evening)
            if rng.random() < 0.5:  # 50% during peak return times
                # Prefer evening returns (15-21), bias toward earlier
                window_hours = total_minutes / 60.0
                target_offset_hours = rng.uniform(0, min(window_hours, 6.0))
                depart_offset_min = int(target_offset_hours * 60) + rng.randint(-30, 30)
                depart_offset_min = max(0, min(total_minutes, depart_offset_min))
            else:
                # Uniform distribution for other times
                depart_offset_min = rng.randint(0, total_minutes)
            
            departure = earliest + timedelta(minutes=depart_offset_min)
            
            # Realistic flight duration based on route
            flight_duration = _estimate_flight_duration(origin, destination, rng)
            arrival = departure + timedelta(minutes=flight_duration)

            # Realistic aircraft capacity
            capacity, aircraft_type = _get_aircraft_capacity(rng)
            
            # Flight numbers vary by time of day
            hour = departure.hour
            base_flight_num = 5000 + (hour * 50) + (i % 50)
            flight_number = f"AS{base_flight_num}"

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
