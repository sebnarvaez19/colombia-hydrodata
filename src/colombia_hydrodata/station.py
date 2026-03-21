from dataclasses import dataclass
from datetime import datetime
from typing import Self

import pandas as pd

from colombia_hydrodata.attributes import Hydrographic, Location, Variable
from colombia_hydrodata.utils.fetch.aquarius import station_datasets
from colombia_hydrodata.utils.fetch.stations import station_data, station_hydrographic_data, station_location_data


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
    location: Location
    hydrographic: Hydrographic
    variables: dict[str, Variable] | None = None

    @classmethod
    def from_stations_df(cls, station_id: str) -> Self:
        sd = station_data(station_id)
        ld = station_location_data(station_id)
        hd = station_hydrographic_data(station_id)
        vars = {key: Variable(param=value["param"], label=value["label"], id=value["id"]) for key, value in station_datasets(station_id).items()}

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
            location=Location(ld["altitude"], ld["longitude"], ld["latitude"]),
            hydrographic=Hydrographic(hd["hydrographic_area"], hd["hydrographic_zone"], hd["hydrographic_subzone"]),
            variables=vars,
        )


if __name__ == "__main__":
    station = Station.from_stations_df("29037020")
    print(station)
