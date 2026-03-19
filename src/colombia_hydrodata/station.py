from dataclasses import dataclass
from datetime import datetime
from typing import Self

from colombia_hydrodata.utils.fetch.stations import station_data, station_hydrographic_data, station_location_data


@dataclass(frozen=True)
class StationLocation:
    altitude: float
    longitude: float
    latitude: float

    @classmethod
    def from_stations_df(cls, station_id: str) -> Self:
        ld = station_location_data(station_id)
        return cls(altitude=ld["altitude"], longitude=ld["longitude"], latitude=ld["latitude"])


@dataclass(frozen=True)
class StationHydrographic:
    hydrographic_area: str
    hydrographic_zone: str
    hydrigraphic_subzone: str

    @classmethod
    def from_stations_df(cls, station_id: str) -> Self:
        hd = station_hydrographic_data(station_id)
        return cls(hydrographic_area=hd["hydrographic_area"], hydrographic_zone=hd["hydrographic_zone"], hydrigraphic_subzone=hd["hydrographic_subzone"])


@dataclass(frozen=True)
class Station:
    id: str
    name: str
    category: str
    technology: str
    status: str
    department: str
    municipality: str
    installation_date: datetime | None
    suspension_date: datetime | None
    owner: str
    location: StationLocation
    hydrographic: StationHydrographic

    @classmethod
    def from_stations_df(cls, station_id: str) -> Self:
        sd = station_data(station_id)
        ld = station_location_data(station_id)
        hd = station_hydrographic_data(station_id)

        return cls(
            id=sd["id"],
            name=sd["name"],
            category=sd["category"],
            technology=sd["technology"],
            status=sd["status"],
            department=sd["department"],
            municipality=sd["municipality"],
            installation_date=sd["installation_date"],
            suspension_date=sd["suspension_date"],
            owner=sd["owner"],
            location=StationLocation(altitude=ld["altitude"], longitude=ld["longitude"], latitude=ld["latitude"]),
            hydrographic=StationHydrographic(
                hydrographic_area=hd["hydrographic_area"], hydrographic_zone=hd["hydrographic_zone"], hydrigraphic_subzone=hd["hydrographic_subzone"]
            ),
        )


if __name__ == "__main__":
    from colombia_hydrodata.utils.fetch.stations import fetch_df

    stations_df = fetch_df()
    station = Station.from_stations_df("29037020")
    print(station)
