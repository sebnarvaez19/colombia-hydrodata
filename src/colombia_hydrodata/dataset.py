from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Self

import pandas as pd

from colombia_hydrodata.attributes import Variable
from colombia_hydrodata.plot import DatasetPlot
from colombia_hydrodata.utils import tsa
from colombia_hydrodata.utils.fetch.aquarius import dataset
from colombia_hydrodata.utils.keys import time_precision_options

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
            f"Dataset from Station {self.station.name}: {self.station.id}",
            f"{self.station.municipality} ({self.station.department})",
            f"{self.variable}",
        ]

        return ", ".join(parts)

    def sight_level(self, level: float) -> Self:
        """Adjust observed stage values by subtracting the sight level reference.

        The sight level is the difference between the observable (staff gauge)
        reading and the absolute sea-level elevation of the zero mark. Applying
        it converts raw gauge readings into elevation-referenced stage values,
        enabling meaningful comparison of water levels across stations along
        the same river reach.

        Note:
            This method is intended exclusively for stage datasets, i.e.
            variables whose key starts with ``'NIVEL'``. Applying it to other
            variable types produces meaningless results.

        Args:
            level: The sight level offset (in the same units as the observed
                values, typically metres) to subtract from every observation.

        Returns:
            A new Dataset instance with adjusted ``value`` column, leaving
            the original unchanged.
        """
        new_data = self.data.copy()
        new_data["value"] = new_data["value"] - level
        return replace(self, data=new_data)

    def rescale(self, scale: float) -> Self:
        """Convert observed values from one measurement unit to another.

        Multiplies every value in the series by a conversion factor, allowing
        unit transformations without altering the underlying data source.

        Example:
            To convert stage readings from centimetres to metres::

                dataset.rescale(1 / 100)

        Args:
            scale: The multiplicative conversion factor to apply to all
                observed values. Must be set by the caller according to the
                desired unit transformation (e.g. ``1/100`` for cm → m,
                ``1/1000`` for mm → m).

        Returns:
            A new Dataset instance with rescaled ``value`` column, leaving
            the original unchanged.
        """
        new_data = self.data.copy()
        new_data["value"] = new_data["value"] * scale
        return replace(self, data=new_data)

    def interpolate(self, time_precision: str | None = None, **kwargs) -> Self:
        """Resample the time series to a regular frequency and interpolate missing values.

        Resamples the dataset to a uniform time grid, introducing ``NaN`` at
        any timestamps where no measurement was recorded, then fills those gaps
        using :meth:`pandas.DataFrame.interpolate`.

        The target frequency can be supplied explicitly or derived automatically
        from the variable label. Variable labels follow the convention
        ``"<PARAM>_<FREQ>"``, where ``<FREQ>`` is a single-character code
        (``'A'`` annual, ``'M'`` monthly, ``'D'`` daily, ``'H'`` hourly) that
        is mapped to the corresponding pandas offset alias via
        ``time_precision_options``.

        Args:
            time_precision: A pandas offset alias (e.g. ``'D'``, ``'ME'``,
                ``'H'``) that defines the target resampling frequency. If
                ``None``, the frequency is inferred from the trailing segment
                of ``self.variable.label``.
            **kwargs: Additional keyword arguments forwarded to
                :meth:`pandas.DataFrame.interpolate` (e.g. ``method='linear'``,
                ``limit=3``).

        Returns:
            A new Dataset instance with a regularly spaced ``timestamp`` index
            and interpolated ``value`` column, leaving the original unchanged.

        Raises:
            ValueError: If ``time_precision`` is ``None`` and the variable
                label does not contain a recognised time-precision code.
        """
        new_data = self.data.copy()
        if not time_precision:
            ts = self.variable.label.split("_")[-1]
            try:
                time_precision = time_precision_options[ts]
            except KeyError:
                raise ValueError("Variable does not store time precision, please set the value")
        new_data = new_data.set_index("timestamp").resample(time_precision).asfreq().interpolate(**kwargs).reset_index()
        return replace(self, data=new_data)

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

    @property
    def plot(self) -> DatasetPlot:
        """Return a plotting helper bound to this dataset.

        Provides convenient access to the plotting API via
        ``dataset.plot.<method>()`` without storing plotting logic directly on
        the dataset class itself.

        Returns:
            A :class:`colombia_hydrodata.plot.DatasetPlot` instance linked to
            the current dataset.
        """
        return DatasetPlot(dataset=self)
