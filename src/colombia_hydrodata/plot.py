from typing import TYPE_CHECKING, Literal, Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
from numpy.typing import NDArray

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
            trend=pd.Series(self.dataset.data["trend"]) if "trend" in self.dataset.data.columns and column_name == "value" else None,
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

    def tsa_classic(self, **kwargs) -> tuple[Figure, NDArray[np.object_]]:
        fig, axs = plt.subplots(4, 1, **kwargs)
        axs = axs.reshape(-1)

        axs[0] = self.time_series(ax=axs[0])
        axs[1] = self.time_series(column_name="detrended", ax=axs[1])
        axs[2] = self.monthly_data_series(column_name="detrended", ax=axs[2])
        axs[3] = self.stem_series(column_name="anomalies", ax=axs[3])

        for ax in axs:
            ax.set_xlabel("")
        fig.align_labels()
        fig.supxlabel("Timestamp")

        return fig, axs

    def tsa_new(self, **kwargs) -> tuple[Figure, NDArray[np.object_]]:
        fig = plt.figure(**kwargs)
        gs = GridSpec(2, 2, width_ratios=[3, 1])

        ax0 = self.time_series(ax=fig.add_subplot(gs[0, 0]))
        ax0.set(ylabel="Data", xlabel="Timestamp")
        ax1 = self.histogram(column_name="detrended", ax=fig.add_subplot(gs[0, 1]))
        ax1.set(ylabel="Frequency", xlabel="Variability")
        ax2 = self.stem_series(column_name="anomalies", ax=fig.add_subplot(gs[1, 0]))
        ax2.set(ylabel="Anomalies", xlabel="Timestamp")
        ax3 = self.monthly_data_series(column_name="detrended", ax=fig.add_subplot(gs[1, 1]))
        ax3.set(ylabel="Seasonal", xlabel="Month")

        fig.align_labels()

        return fig, np.array([ax0, ax1, ax2, ax3])

    def time_series_analysis(self, layout: Literal["classic", "new"] = "new", **kwargs) -> tuple[Figure, NDArray[np.object_]]:
        match layout:
            case "classic":
                return self.tsa_classic(**kwargs)
            case "new":
                return self.tsa_new(**kwargs)
            case _:
                raise ValueError("Layaout must be 'classic' or 'new'.")

    def daily_series_analysis(
        self,
        column_name: str = "value",
        years: Sequence[int] | None = None,
        **kwargs,
    ) -> tuple[Figure, NDArray[np.object_]]:
        fig = plt.figure(**kwargs)
        gs = GridSpec(1, 2, width_ratios=[3, 1])

        ax0 = self.annual_data_series(column_name, years=years, ax=fig.add_subplot(gs[0, 0]))
        ax0.set(ylabel="Data")
        ax1 = self.histogram(column_name, orientation="y", ax=fig.add_subplot(gs[0, 1]))
        ax1.set(ylabel="", xlabel="Frequency")
        ax1.sharey(ax0)

        return fig, np.array([ax0, ax1])


if __name__ == "__main__":
    from colombia_hydrodata import Station

    station = Station.from_stations_df("29037020")
    dataset = station.fetch("NIVEL@NV_MEDIA_D").sight_level(-0.367).rescale(1 / 100).interpolate().deconstruction()
    ds_plot = DatasetPlot(dataset)

    def test_tsa():
        ds_plot.time_series_analysis(figsize=(10, 6), tight_layout=True)

    def test_tsa_stripes():
        _, axs = ds_plot.daily_series_analysis(years=[2026, 2011], figsize=(10, 4), tight_layout=True)
        axs[0].legend()

    test_tsa()
    test_tsa_stripes()
    plt.show()
