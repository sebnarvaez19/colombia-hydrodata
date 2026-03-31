from typing import TYPE_CHECKING, Literal

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from colombia_hydrodata.utils import plot

if TYPE_CHECKING:
    from colombia_hydrodata.dataset import Dataset


class DatasetPlot:
    def __init__(self, dataset: "Dataset") -> None:
        self.dataset = dataset

    def time_series(self, column_name: str = "value", **kwargs) -> Axes:
        return plot.time_series(
            timestamp=self.dataset.data["timestamp"],
            value=self.dataset.data[column_name],
            trend=self.dataset.data["trend"] if "trend" in self.dataset.data.columns else None,
            **kwargs,
        )

    def stem_series(self, column_name: str = "value", **kwargs) -> Axes:
        return plot.stem_series(timestamp=self.dataset.data["timestamp"], value=self.dataset.data[column_name], **kwargs)

    def histogram(self, column_name: str = "value", **kwargs) -> Axes:
        return plot.histogram(value=self.dataset.data[column_name], **kwargs)

    def monthly_data_series(self, column_name: str = "value", **kwargs) -> Axes:
        return plot.month_series(timestamp=self.dataset.data["timestamp"], value=self.dataset.data[column_name], **kwargs)

    def annual_data_series(self, column_name: str = "value", **kwargs) -> Axes:
        return plot.year_series(timestamp=self.dataset.data["timestamp"], value=self.dataset.data[column_name], **kwargs)

    def seasonal_data_series(self, column_name: str = "value", time_resolution: Literal["month", "year"] = "month", **kwargs) -> Axes:
        if time_resolution == "month":
            return plot.month_series(
                timestamp=self.dataset.data["timestamp"],
                value=self.dataset.data[column_name],
                **kwargs,
            )
        if time_resolution == "year":
            return plot.year_series(
                timestamp=self.dataset.data["timestamp"],
                value=self.dataset.data[column_name],
                **kwargs,
            )
        raise ValueError("time_resolution must be either 'month' or 'year'")


if __name__ == "__main__":
    from colombia_hydrodata import Station

    fig, axs = plt.subplots(2, 2, figsize=(10, 8), tight_layout=True)
    axs = axs.reshape(-1)

    station = Station.from_stations_df("29037020")
    dataset = station.fetch("NIVEL@NV_MEDIA_D").sight_level(-0.367).rescale(1 / 100).interpolate().deconstruction()
    ds_plot = DatasetPlot(dataset)
    ds_plot.time_series(ax=axs[0])
    ds_plot.histogram(column_name="detrended", bins=50, ax=axs[1])
    ds_plot.stem_series(column_name="anomalies", ax=axs[2])

    plt.show()
