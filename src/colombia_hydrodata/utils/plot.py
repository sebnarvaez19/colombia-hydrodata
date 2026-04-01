from typing import Literal

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.axes import Axes

from colombia_hydrodata.utils.keys import months, months_doy_limits
from colombia_hydrodata.utils.tsa import day_dataframe, day_quantiles


def check_ax(ax: Axes | None) -> Axes:
    return plt.subplots(1, tight_layout=True)[1] if not ax else ax


def time_series(
    timestamp: pd.Series,
    value: pd.Series,
    trend: pd.Series | None = None,
    is_lm: bool = True,
    ax: Axes | None = None,
    **kwargs,
) -> Axes:
    ax = check_ax(ax)
    ax = sns.lineplot(x=timestamp, y=value, ax=ax)
    if isinstance(trend, pd.Series) and is_lm:
        ax = sns.lineplot(x=timestamp, y=trend, color="gray", linestyle="-", ax=ax)
        m = (trend[len(trend) - 1] - trend[0]) / len(trend)
        b = trend[0]
        ax.text(0.05, 0.95, f"y = {m:.3f}x + {b:.3f}", transform=ax.transAxes, ha="left", va="top")
    ax.set(**kwargs)
    return ax


def histogram(value: pd.Series, orientation: Literal["x", "y"] = "x", bins: int = 30, ax: Axes | None = None, **kwargs) -> Axes:
    ax = check_ax(ax)
    ax = sns.histplot(**{orientation: value}, bins=bins, kde=True, stat="percent", ax=ax)  # type: ignore
    ax.set(**kwargs)
    return ax


def stem_series(timestamp: pd.Series, value: pd.Series, ax: Axes | None = None, **kwargs) -> Axes:
    ax = check_ax(ax)
    ax = sns.scatterplot(x=timestamp, y=value, ax=ax)
    ax.stem(timestamp, value, linefmt="black", markerfmt="")
    ax.set(**kwargs)
    return ax


def month_series(
    timestamp: pd.Series,
    value: pd.Series,
    ax: Axes | None = None,
    month_size: int = 1,
    month_rotation: float = 0.0,
    **kwargs,
) -> Axes:
    month = timestamp.dt.month
    ax = time_series(month, value, ax=ax, **kwargs)
    ax.set_xticks(ticks=range(1, 13), labels=[m[:month_size] for m in months], rotation=month_rotation)
    return ax


def year_series(timestamp: pd.Series, value: pd.Series, ax: Axes | None = None, color: str | None = None, **kwargs) -> Axes:
    ax = check_ax(ax)
    color = color or ax._get_lines.get_next_color()  # type: ignore

    for mdl in months_doy_limits:
        ax.axvline(x=mdl, color="black", linestyle="-", linewidth=0.5, alpha=0.5)

    df = day_quantiles(day_dataframe(timestamp, value))
    ax.fill_between(df["doy"], df["value_0.0"], df["value_0.1"], color=color, alpha=0.2)
    ax.fill_between(df["doy"], df["value_0.1"], df["value_0.25"], color=color, alpha=0.3)
    ax.fill_between(df["doy"], df["value_0.75"], df["value_0.9"], color=color, alpha=0.3)
    ax.fill_between(df["doy"], df["value_0.9"], df["value_1.0"], color=color, alpha=0.2)
    ax.fill_between(df["doy"], df["value_0.25"], df["value_0.75"], color=color, alpha=0.4)
    ax.plot(df["doy"], df["value_0.5"], color=color)

    def set_label(col_name: str):
        q = float(col_name.split("_")[-1])
        return "Max" if q == 1.0 else "Min" if q == 0.0 else str(round((1 - q) * 100)) + "%"

    for col_name in [c for c in df.columns if c.startswith("value_")]:
        ax.text(x=360, y=df[col_name][len(df) - 1], s=f"{set_label(col_name)}", fontsize="small", ha="right", va="center")

    ax.set_xticks(ticks=[mdl - 15 for mdl in months_doy_limits], labels=months)
    ax.set(**kwargs)
    ax.set(xlim=[1, 365])
    return ax


def year_line(timestamp: pd.Series, value: pd.Series, year: int, ax: Axes | None = None, **kwargs) -> Axes:
    ax = check_ax(ax)
    df = day_dataframe(timestamp, value)
    df = df[df["year"] == year]
    ax.plot(df["doy"], df["value"], label=f"{year}", **kwargs)
    return ax


if __name__ == "__main__":
    from colombia_hydrodata import Station

    station = Station.from_stations_df("29037020")
    dataset = station.fetch("NIVEL@NV_MEDIA_D").sight_level(-0.367).rescale(1 / 100).interpolate().deconstruction()
    # time_series(dataset.data["timestamp"], dataset.data["value"], dataset.data["trend"])
    # histogram(dataset.data["detrended"], orientation="y", bins=50)
    # stem_series(dataset.data["timestamp"], dataset.data["anomalies"])
    # month_series(dataset.data["timestamp"], dataset.data["detrended"])
    ax = year_series(dataset.data["timestamp"], dataset.data["value"])
    ax = year_line(dataset.data["timestamp"], dataset.data["value"], 2026, ax=ax, color="C2", label="2026")
    ax.legend()
    plt.show()
