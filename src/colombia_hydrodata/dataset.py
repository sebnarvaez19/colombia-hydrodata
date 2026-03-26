from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

import pandas as pd

from colombia_hydrodata.attributes import Variable
from colombia_hydrodata.utils.fetch.aquarius import dataset
from colombia_hydrodata.utils import tsa

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

    def detrend(self, **kwargs) -> "Dataset":
        trend, detrended = tsa.detrend(self.data["value"].copy(), **kwargs)
        self.data["trend"] = trend
        self.data["detrended"] = detrended
        return self

    def seasonal(self) -> "Dataset":
        if "detrended" not in self.data.columns:
            raise KeyError("Detrend process must be performed")
        seasonal = tsa.seasonal_series(self.data["detrended"].copy(), self.data["timestamp"].copy())
        self.data["seasonal"] = seasonal
        return self

    def anomalies(self) -> "Dataset":
        if "seasonal" not in self.data.columns:
            raise KeyError("Seasonal process must be performed")
        anomalies = tsa.anomalies_series(self.data["detrended"].copy(), self.data["seasonal"].copy())
        self.data["anomalies"] = anomalies
        return self

    def deconstruction(self, **kwargs) -> "Dataset":
        self.data = tsa.deconstruction(self.data["value"].copy(), self.data["timestamp"].copy(), **kwargs)
        return self
