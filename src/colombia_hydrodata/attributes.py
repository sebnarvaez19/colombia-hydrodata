from dataclasses import dataclass
from typing import Self

from colombia_hydrodata.utils.fetch.stations import station_hydrographic_data, station_location_data


@dataclass(frozen=True)
class Location:
    """Geographic location attributes of a station.

    Attributes:
        altitude: Elevation of the station above sea level, in meters.
        longitude: Longitudinal coordinate of the station, in decimal degrees.
        latitude: Latitudinal coordinate of the station, in decimal degrees.
    """

    altitude: float
    longitude: float
    latitude: float

    def __str__(self) -> str:
        """Return a human-readable string representation of the location.

        Returns:
            A formatted string showing altitude, longitude, and latitude.
        """
        return f"Location: altitude={self.altitude:0.2f} [{self.longitude:0.3f}; {self.latitude:0.3f}]"

    @classmethod
    def from_stations_df(cls, station_id: str) -> Self:
        """Construct a Location instance from station location data.

        Fetches location data for the given station ID and uses it to
        populate the altitude, longitude, and latitude fields.

        Args:
            station_id: The unique identifier of the station.

        Returns:
            A new Location instance populated with the station's location data.
        """
        ld = station_location_data(station_id)
        return cls(altitude=ld["altitude"], longitude=ld["longitude"], latitude=ld["latitude"])


@dataclass(frozen=True)
class Hydrographic:
    """Hydrographic classification attributes of a station.

    Attributes:
        hydrographic_area: The broad hydrographic area the station belongs to.
        hydrographic_zone: The hydrographic zone within the area.
        hydrographic_subzone: The hydrographic subzone within the zone.
    """

    hydrographic_area: str
    hydrographic_zone: str
    hydrographic_subzone: str

    def __str__(self) -> str:
        """Return a human-readable string representation of the hydrographic data.

        Returns:
            A formatted string showing the hydrographic area, zone, and subzone.
        """
        return f"Hydrographic: area={self.hydrographic_area} zone={self.hydrographic_zone} subzone={self.hydrographic_subzone}"

    @classmethod
    def from_stations_df(cls, station_id: str) -> Self:
        """Construct a Hydrographic instance from station hydrographic data.

        Fetches hydrographic data for the given station ID and uses it to
        populate the area, zone, and subzone fields.

        Args:
            station_id: The unique identifier of the station.

        Returns:
            A new Hydrographic instance populated with the station's
            hydrographic classification data.
        """
        hd = station_hydrographic_data(station_id)
        return cls(hydrographic_area=hd["hydrographic_area"], hydrographic_zone=hd["hydrographic_zone"], hydrographic_subzone=hd["hydrographic_subzone"])


@dataclass(frozen=True)
class Variable:
    """A measured hydrometeorological variable.

    Attributes:
        param: Short parameter code identifying the type of variable
            (e.g. ``"precipitation"``, ``"streamflow"``).
        label: Descriptive label for the variable, typically including
            sensor or aggregation details.
        id: Numeric identifier for the variable as used by the data source.
    """

    param: str
    label: str
    id: int

    def __str__(self) -> str:
        """Return an uppercase string combining the param and label.

        Returns:
            A string of the form ``"PARAM@LABEL"`` in uppercase.
        """
        return f"{self.param}@{self.label}".upper()
