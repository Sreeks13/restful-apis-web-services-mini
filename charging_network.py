from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class ChargingStation:
    station_id: str
    name: str
    location: str
    available_ports: int
    total_ports: int
    status: str = "online"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ChargingSession:
    session_id: str
    station_id: str
    vehicle_id: str
    status: str = "active"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def is_station_available(station: dict[str, Any]) -> bool:
    return (
        station.get("status") == "online"
        and int(station.get("available_ports", 0)) > 0
    )