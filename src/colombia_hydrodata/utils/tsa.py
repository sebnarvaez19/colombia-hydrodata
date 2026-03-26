from typing import Literal

import numpy as np
import pandas as pd
import statsmodels.api as sm


def lm_trend(value: pd.Series, robust: bool = True) -> pd.Series:
    """Estimate a linear trend using a regression model.

    Args:
        value: Time-series values to fit the trend to.
        robust: If True, uses Huber-T robust linear regression (RLM) to
            reduce the influence of outliers. If False, uses standard OLS.

    Returns:
        A Series of fitted trend values with the same index as ``value``,
        named ``'trend'``.
    """
    exog = sm.add_constant(pd.Series(np.arange(len(value)), index=value.index, name="x"))
    model = sm.RLM(value, exog, M=sm.robust.norms.HuberT() if robust else None)
    results = model.fit()
    return pd.Series(results.predict(exog), index=value.index, name="trend")


def ma_trend(value: pd.Series, window: int = 7) -> pd.Series:
    """Estimate a trend using a centered moving average.

    Args:
        value: Time-series values to smooth.
        window: Number of periods to include in the rolling window.
            Defaults to 7.

    Returns:
        A Series of smoothed trend values with the same index as ``value``,
        named ``'trend'``.
    """
    return pd.Series(value.rolling(window, min_periods=1, center=True).mean(), index=value.index, name="trend")


def detrend(value: pd.Series, trend: pd.Series | Literal["lm", "ma"] = "lm", **kwargs) -> tuple[pd.Series, pd.Series]:
    """Remove a trend component from a time series.

    Args:
        value: Time-series values to detrend.
        trend: The trend to remove. Can be a precomputed ``pd.Series``,
            ``'lm'`` to fit a linear/robust regression trend, or ``'ma'``
            to use a moving average trend. Defaults to ``'lm'``.
        **kwargs: Additional keyword arguments passed to the selected trend
            function (``lm_trend`` or ``ma_trend``).

    Returns:
        A tuple of ``(trend, detrended)`` where ``trend`` is the estimated
        trend series and ``detrended`` is the residual after subtracting it.

    Raises:
        ValueError: If ``trend`` is a ``pd.Series`` with a different length
            than ``value``, or if ``trend`` is not a valid literal.
    """
    if isinstance(trend, pd.Series):
        if len(trend) != len(value):
            raise ValueError("Trend and value must have the same length.")
        return trend, value - trend
    if trend == "lm":
        return lm_trend(value, **kwargs), value - lm_trend(value, **kwargs)
    if trend == "ma":
        return ma_trend(value, **kwargs), value - ma_trend(value, **kwargs)
    raise ValueError(f"Trend must be a pd.Series or 'lm' | 'ma', not {trend} ({type(trend)})")


def seasonal_series(value: pd.Series, timestamp: pd.Series) -> pd.Series:
    """Compute a seasonal component by averaging values per calendar month.

    Args:
        value: Time-series values (typically the detrended series).
        timestamp: Corresponding datetime values used to extract the month.

    Returns:
        A Series of seasonal values with the same index as ``value``,
        named ``'stational_series'``, where each entry is the mean of all
        observations sharing the same calendar month.

    Raises:
        ValueError: If ``timestamp`` and ``value`` have different lengths.
    """
    if len(timestamp) != len(value):
        raise ValueError("Timestamp and value must have the same length.")
    mdf = pd.DataFrame({"m": timestamp.dt.month, "y": value})
    msr = pd.Series(mdf.groupby("m").mean()["y"])
    return pd.Series([msr.loc[ts.month] for ts in timestamp], index=value.index, name="stational_series")


def anomalies_series(value: pd.Series, seasonal_series: pd.Series) -> pd.Series:
    """Compute anomalies by removing the seasonal component from a series.

    Args:
        value: Time-series values (typically the detrended series).
        seasonal_series: Seasonal component to subtract, as returned by
            :func:`seasonal_series`.

    Returns:
        A Series of anomaly values with the same index as ``value``,
        named ``'anomalies_series'``.

    Raises:
        ValueError: If ``seasonal_series`` and ``value`` have different lengths.
    """
    if len(seasonal_series) != len(value):
        raise ValueError("Stational series and value must have the same length.")
    return pd.Series(value - seasonal_series, index=value.index, name="anomalies_series")


def deconstruction(value: pd.Series, timestamp: pd.Series, **kwargs) -> pd.DataFrame:
    """Decompose a time series into trend, seasonal, and anomaly components.

    Runs the full decomposition pipeline: detrending, seasonal estimation,
    and anomaly extraction in a single call.

    Args:
        value: Raw time-series values to decompose.
        timestamp: Corresponding datetime values aligned with ``value``.
        **kwargs: Additional keyword arguments forwarded to :func:`detrend`
            (e.g. ``trend='ma'``, ``window=12``).

    Returns:
        A DataFrame with columns: ``timestamp``, ``value``, ``trend``,
        ``detrended``, ``seasonal``, and ``anomalies``.
    """
    trend, detrended = detrend(value, **kwargs)
    seasonal = seasonal_series(detrended, timestamp)
    anomalies = anomalies_series(detrended, seasonal)
    return pd.DataFrame(
        {
            "timestamp": timestamp,
            "value": value,
            "trend": trend,
            "detrended": detrended,
            "seasonal": seasonal,
            "anomalies": anomalies,
        }
    )
