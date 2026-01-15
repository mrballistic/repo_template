"""Dependency client interfaces for Fly Bot.

Abstract interfaces for external dependencies with mock implementations for testing.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Flight:
    """Flight information."""

    flight_number: str
    origin: str
    destination: str
    departure: datetime
    arrival: datetime
    open_seats: int | None = None
    capacity: int | None = None


@dataclass(frozen=True)
class EmptiesSnapshot:
    """Empties snapshot for outbound flights."""

    snapshot_time: datetime
    flights: list[Flight]
    is_stale: bool = False


class EmptiesClient(ABC):
    """Abstract client for empties/load data."""

    @abstractmethod
    async def get_empties(
        self,
        origin: str,
        destination: str,
        lookahead_minutes: int,
        snapshot_time: datetime,
    ) -> EmptiesSnapshot | None:
        """Fetch empties snapshot for flights departing within lookahead window.
        
        Returns None if service is unavailable.
        """
        pass


class ScheduleClient(ABC):
    """Abstract client for flight schedule data."""

    @abstractmethod
    async def get_return_flights(
        self,
        origin: str,
        destination: str,
        earliest: datetime,
        latest: datetime,
    ) -> list[Flight] | None:
        """Fetch return flight schedule within time window.
        
        Returns None if service is unavailable.
        """
        pass


# Mock implementations for testing


class MockEmptiesClient(EmptiesClient):
    """Mock empties client for testing."""

    def __init__(
        self,
        snapshot: EmptiesSnapshot | None = None,
        fail: bool = False,
    ):
        self._snapshot = snapshot
        self._fail = fail

    async def get_empties(
        self,
        origin: str,
        destination: str,
        lookahead_minutes: int,
        snapshot_time: datetime,
    ) -> EmptiesSnapshot | None:
        """Return configured snapshot or None if failing."""
        if self._fail:
            return None
        return self._snapshot


class MockScheduleClient(ScheduleClient):
    """Mock schedule client for testing."""

    def __init__(
        self,
        flights: list[Flight] | None = None,
        fail: bool = False,
    ):
        self._flights = flights or []
        self._fail = fail

    async def get_return_flights(
        self,
        origin: str,
        destination: str,
        earliest: datetime,
        latest: datetime,
    ) -> list[Flight] | None:
        """Return configured flights or None if failing."""
        if self._fail:
            return None
        return self._flights
