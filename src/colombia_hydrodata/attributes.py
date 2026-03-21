from dataclasses import dataclass
from typing import Self

from colombia_hydrodata.utils.fetch.stations import station_hydrographic_data, station_location_data


@dataclass(frozen=True)
class Location:
    altitude: float
    longitude: float
    latitude: float

    def __str__(self) -> str:
        return f"Location: altitude={self.altitude:0.2f} [{self.longitude:0.3f}; {self.latitude:0.3f}]"

    @classmethod
    def from_stations_df(cls, station_id: str) -> Self:
        ld = station_location_data(station_id)
        return cls(altitude=ld["altitude"], longitude=ld["longitude"], latitude=ld["latitude"])


@dataclass(frozen=True)
class Hydrographic:
    hydrographic_area: str
    hydrographic_zone: str
    hydrigraphic_subzone: str

    def __str__(self) -> str:
        return f"Hydrographic: area={self.hydrographic_area} zone={self.hydrographic_zone} subzone={self.hydrigraphic_subzone}"

    @classmethod
    def from_stations_df(cls, station_id: str) -> Self:
        hd = station_hydrographic_data(station_id)
        return cls(hydrographic_area=hd["hydrographic_area"], hydrographic_zone=hd["hydrographic_zone"], hydrigraphic_subzone=hd["hydrographic_subzone"])


@dataclass(frozen=True)
class Variable:
    param: str
    label: str
    id: int

    def __str__(self) -> str:
        return f"{self.param}@{self.label}".upper()
