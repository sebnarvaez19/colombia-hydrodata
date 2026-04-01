from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Self

import pandas as pd

from colombia_hydrodata.attributes import Hydrographic, Location, Variable
from colombia_hydrodata.utils.fetch.aquarius import station_datasets
from colombia_hydrodata.utils.fetch.stations import station_data, station_hydrographic_data, station_location_data

if TYPE_CHECKING:
    from colombia_hydrodata.dataset import Dataset


@dataclass(frozen=True)
class Station:
    """Immutable representation of a hydrometeorological monitoring station.

    Holds all descriptive metadata for a station retrieved from the IDEAM
    data services, including administrative, geographic, hydrographic, and
    variable information.

    Attributes:
        id: Unique station identifier code.
        name: Human-readable station name.
        category: Station category (e.g. climática, limnigráfica).
        technology: Data-collection technology used at the station.
        status: Operational status of the station (e.g. Activa, Suspendida).
        department: Colombian department where the station is located.
        municipality: Municipality where the station is located.
        installation_date: Date the station was commissioned, or ``None`` if unknown.
        suspension_date: Date the station was decommissioned, or ``None`` if still active.
        owner: Entity responsible for the station.
        location: Geographic coordinates and altitude of the station.
        hydrographic: Hydrographic area, zone, and sub-zone of the station.
        variables: Mapping of variable keys to their ``Variable`` descriptors,
            or ``None`` if no variable information is available.
    """

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
        """Construct a Station by fetching all metadata from remote data services.

        Calls the station, location, hydrographic, and Aquarius dataset
        endpoints in sequence and assembles a fully populated ``Station``
        instance from the combined responses.

        Args:
            station_id: The unique identifier code of the station to fetch.

        Returns:
            A fully populated ``Station`` instance for the requested station.
        """
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

    def _resolve_variable(self, key: str) -> Variable:
        """Look up a Variable by key, normalising to upper-case.

        Args:
            key: Variable key, case-insensitive (e.g. ``"NIVEL@NV_MEDIA_D"``).

        Returns:
            The matching ``Variable`` descriptor.

        Raises:
            TypeError: If the station has no variables.
            KeyError: If *key* is not found among the available variables.
        """
        key = key.upper()
        if not self.variables:
            raise TypeError("There are no variables for this station.")
        try:
            return self.variables[key]
        except KeyError:
            raise KeyError(f"Variable {key} not found. Available variables: {', '.join(self.variables.keys())}")

    def __contains__(self, key: str) -> bool:
        """Return ``True`` if *key* identifies a valid variable on this station.

        Args:
            key: Variable key to test, case-insensitive.

        Returns:
            ``True`` if the key resolves to a variable, ``False`` otherwise.
        """
        try:
            self._resolve_variable(key)
            return True
        except Exception:
            return False

    def fetch(self, key: str) -> "Dataset":
        """Retrieve the dataset for a given variable key.

        Args:
            key: Variable key, case-insensitive (e.g. ``"NIVEL@NV_MEDIA_D"``).

        Returns:
            A ``Dataset`` populated with observations for the requested variable.

        Raises:
            TypeError: If the station has no variables.
            KeyError: If *key* is not found among the available variables.
        """
        from colombia_hydrodata.dataset import Dataset

        variable = self._resolve_variable(key)
        return Dataset.from_variable(self, variable)  # type: ignore

    def __getitem__(self, key: str) -> "Dataset":
        """Retrieve the dataset for *key* using bracket notation.

        Delegates to :meth:`fetch`.

        Args:
            key: Variable key, case-insensitive (e.g. ``"NIVEL@NV_MEDIA_D"``).

        Returns:
            A ``Dataset`` populated with observations for the requested variable.
        """
        return self.fetch(key)

    def __str__(self) -> str:
        """Return a human-readable summary of the station.

        Returns:
            A multi-line string showing the station's name, identifier,
            location, status, operational dates, owner, hydrographic context,
            and available variables grouped by measurement type.
        """
        parts = [
            f"Station {self.name}: {self.id}",
            f"  {self.municipality} ({self.department})",
            f"  Info: {self.status} {self.category} ({self.technology})",
            f"  Time: {self.installation_date} - {'ongoing' if pd.isnull(self.suspension_date) else self.suspension_date}",  # type: ignore
            f"  Owner: {self.owner}",
            f"  {self.location}",
            f"  {self.hydrographic}",
            "  Variables:",
        ]
        if self.variables:
            groups: dict[str, list[str]] = {}
            for var in self.variables:
                group, _, label = var.partition("@")
                groups.setdefault(group, []).append(label)
            for group, labels in groups.items():
                parts.append(f"    {group}:")
                parts.append(f"       {', '.join(labels)}")
        return "\n".join(parts)


if __name__ == "__main__":
    station = Station.from_stations_df("29037020")
    print(station)
    print(station["NIVEL@NV_MEDIA_D"])
