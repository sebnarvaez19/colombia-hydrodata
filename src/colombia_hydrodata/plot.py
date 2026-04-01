from typing import TYPE_CHECKING, Literal, Sequence

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes

from colombia_hydrodata.utils import plot

if TYPE_CHECKING:
    from colombia_hydrodata.dataset import Dataset


class DatasetPlot:
    def __init__(self, dataset: "Dataset") -> None:
        self.dataset = dataset

    def time_series(self, column_name: str = "value", **kwargs) -> Axes:
        return plot.time_series(
            timestamp=pd.Series(self.dataset.data["timestamp"]),
            value=pd.Series(self.dataset.data[column_name]),
            trend=pd.Series(self.dataset.data["trend"]) if "trend" in self.dataset.data.columns else None,
            **kwargs,
        )

    def stem_series(self, column_name: str = "value", **kwargs) -> Axes:
        return plot.stem_series(
            timestamp=pd.Series(self.dataset.data["timestamp"]), value=pd.Series(self.dataset.data[column_name]), **kwargs
        )

    def histogram(self, column_name: str = "value", **kwargs) -> Axes:
        return plot.histogram(value=pd.Series(self.dataset.data[column_name]), **kwargs)

    def monthly_data_series(self, column_name: str = "value", **kwargs) -> Axes:
        return plot.month_series(
            timestamp=pd.Series(self.dataset.data["timestamp"]), value=pd.Series(self.dataset.data[column_name]), **kwargs
        )

    def annual_data_series(self, column_name: str = "value", years: Sequence[int] | None = None, **kwargs) -> Axes:
        ax = plot.year_series(
            timestamp=pd.Series(self.dataset.data["timestamp"]), value=pd.Series(self.dataset.data[column_name]), **kwargs
        )
        if years and all(map(lambda x: isinstance(x, int), years)):
            for year in years:
                ax = plot.year_line(
                    timestamp=pd.Series(self.dataset.data["timestamp"]), value=pd.Series(self.dataset.data[column_name]), year=year, ax=ax
                )
        return ax

    def seasonal_data_series(self, column_name: str = "value", time_resolution: Literal["month", "year"] = "month", **kwargs) -> Axes:
        match time_resolution:
            case "month":
                return plot.month_series(
                    timestamp=pd.Series(self.dataset.data["timestamp"]),
                    value=pd.Series(self.dataset.data[column_name]),
                    **kwargs,
                )
            case "year":
                return plot.year_series(
                    timestamp=pd.Series(self.dataset.data["timestamp"]),
                    value=pd.Series(self.dataset.data[column_name]),
                    **kwargs,
                )
            case _:
                raise ValueError("time_resolution must be either 'month' or 'year'")


if __name__ == "__main__":
    from colombia_hydrodata import Station

    station = Station.from_stations_df("29037020")
    dataset = station.fetch("NIVEL@NV_MEDIA_D").sight_level(-0.367).rescale(1 / 100).interpolate().deconstruction()
    ds_plot = DatasetPlot(dataset)

    def test_tsa_basic_plots():
        _, axs = plt.subplots(2, 2, figsize=(10, 8), tight_layout=True)
        axs = axs.reshape(-1)

        ds_plot.time_series(ax=axs[0])
        ds_plot.histogram(column_name="detrended", bins=50, ax=axs[1])
        ds_plot.stem_series(column_name="anomalies", ax=axs[2])
        ds_plot.seasonal_data_series(column_name="detrended", time_resolution="month", ax=axs[3])

    def test_tsa_stripes():
        _, axs = plt.subplots(2, 2, figsize=(10, 8), tight_layout=True)
        axs = axs.reshape(-1)

        ds_plot.annual_data_series(column_name="value", years=[2026, 2024, 2011], ax=axs[0])
        ds_plot.histogram(column_name="value", bins=50, orientation="y", ax=axs[1])
        ds_plot.annual_data_series(column_name="detrended", ax=axs[2])
        ds_plot.histogram(column_name="detrended", bins=50, orientation="y", ax=axs[3])

    test_tsa_stripes()
    plt.show()
