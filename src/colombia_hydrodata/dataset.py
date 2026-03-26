from dataclasses import dataclass, replace
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

    def detrend(self, **kwargs) -> Self:
        """Remove the trend component from the dataset's value series.

        Delegates to :func:`colombia_hydrodata.utils.tsa.detrend`. The
        resulting trend and detrended columns are added to a copy of the
        underlying DataFrame.

        Args:
            **kwargs: Keyword arguments forwarded to
                :func:`~colombia_hydrodata.utils.tsa.detrend` (e.g.
                ``trend='ma'``, ``window=12``).

        Returns:
            A new Dataset instance with ``trend`` and ``detrended`` columns
            appended to the data, leaving the original unchanged.
        """
        new_data = self.data.copy()
        trend, detrended = tsa.detrend(new_data["value"], **kwargs)
        new_data["trend"] = trend
        new_data["detrended"] = detrended
        return replace(self, data=new_data)

    def seasonal(self) -> Self:
        """Compute the seasonal component from the detrended series.

        Delegates to :func:`colombia_hydrodata.utils.tsa.seasonal_series`.
        Must be called after :meth:`detrend`.

        Returns:
            A new Dataset instance with a ``seasonal`` column appended to
            the data, leaving the original unchanged.

        Raises:
            KeyError: If the ``detrended`` column is not present in the data.
        """
        if "detrended" not in self.data.columns:
            raise KeyError("Detrend process must be performed")
        new_data = self.data.copy()
        new_data["seasonal"] = tsa.seasonal_series(new_data["detrended"], new_data["timestamp"])
        return replace(self, data=new_data)

    def anomalies(self) -> Self:
        """Compute anomalies by removing the seasonal component.

        Delegates to :func:`colombia_hydrodata.utils.tsa.anomalies_series`.
        Must be called after :meth:`seasonal`.

        Returns:
            A new Dataset instance with an ``anomalies`` column appended to
            the data, leaving the original unchanged.

        Raises:
            KeyError: If the ``seasonal`` column is not present in the data.
        """
        if "seasonal" not in self.data.columns:
            raise KeyError("Seasonal process must be performed")
        new_data = self.data.copy()
        new_data["anomalies"] = tsa.anomalies_series(new_data["detrended"], new_data["seasonal"])
        return replace(self, data=new_data)

    def deconstruction(self, **kwargs) -> Self:
        """Fully decompose the value series in a single step.

        Delegates to :func:`colombia_hydrodata.utils.tsa.deconstruction`,
        running detrending, seasonal estimation, and anomaly extraction at
        once. Replaces the entire DataFrame with the decomposition result.

        Args:
            **kwargs: Keyword arguments forwarded to
                :func:`~colombia_hydrodata.utils.tsa.deconstruction` (e.g.
                ``trend='ma'``, ``window=12``).

        Returns:
            A new Dataset instance whose data contains columns: ``timestamp``,
            ``value``, ``trend``, ``detrended``, ``seasonal``, and
            ``anomalies``.
        """
        new_data = tsa.deconstruction(self.data["value"].copy(), self.data["timestamp"].copy(), **kwargs)
        return replace(self, data=new_data)
