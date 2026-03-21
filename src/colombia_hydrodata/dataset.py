from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

import pandas as pd

from colombia_hydrodata.attributes import Variable
from colombia_hydrodata.utils.fetch.aquarius import dataset

if TYPE_CHECKING:
    from colombia_hydrodata.station import Station


@dataclass
class Dataset:
    """Holds time-series data for a single variable measured at a station.

    Attributes:
        station: The station at which the variable was measured.
        variable: The hydrological or meteorological variable being recorded.
        data: A DataFrame containing the time-series observations for the
            variable, as retrieved from the Aquarius data source.
    """

    station: "Station"
    variable: Variable
    data: pd.DataFrame

    @classmethod
    def from_variable(cls, station: "Station", variable: Variable) -> Self:
        """Construct a Dataset by fetching data for the given variable from Aquarius.

        Args:
            station: The station associated with the variable.
            variable: The variable whose time-series data should be fetched.

        Returns:
            A new Dataset instance populated with the fetched data.
        """
        return cls(station, variable, dataset(variable.id))

    def __str__(self) -> str:
        """Return a human-readable summary of the dataset.

        Returns:
            A comma-separated string containing the station name, station ID,
            municipality, department, and variable description.
        """
        parts = [
            f"Datset from Station {self.station.name}: {self.station.id}",
            f"{self.station.municipality} ({self.station.department})",
            f"{self.variable}",
        ]

        return ", ".join(parts)
