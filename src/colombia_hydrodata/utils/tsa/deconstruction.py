from typing import Literal

import numpy as np
import pandas as pd
import statsmodels.api as sm


def lm_trend(value: pd.Series, robust: bool = True) -> pd.Series:
    exog = sm.add_constant(pd.Series(np.arange(len(value)), index=value.index, name="x"))
    model = sm.RLM(value, exog, M=sm.robust.norms.HuberT() if robust else None)
    results = model.fit()
    return pd.Series(results.predict(exog), index=value.index, name="trend")


def ma_trend(value: pd.Series, window: int = 7) -> pd.Series:
    return pd.Series(value.rolling(window, min_periods=1, center=True).mean(), index=value.index, name="trend")


def detrend(value: pd.Series, trend: pd.Series | Literal["lm", "ma"] = "lm", **kwargs) -> tuple[pd.Series, pd.Series]:
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
    if len(timestamp) != len(value):
        raise ValueError("Timestamp and value must have the same length.")
    mdf = pd.DataFrame({"m": timestamp.dt.month, "y": value})
    msr = pd.Series(mdf.groupby("m").mean()["y"])
    return pd.Series([msr.loc[ts.month] for ts in timestamp], index=value.index, name="stational_series")


def anomalies_series(value: pd.Series, seasonal_series: pd.Series) -> pd.Series:
    if len(seasonal_series) != len(value):
        raise ValueError("Stational series and value must have the same length.")
    return pd.Series(value - seasonal_series, index=value.index, name="anomalies_series")


def deconstruction(value: pd.Series, timestamp: pd.Series, **kwargs) -> pd.DataFrame:
    trend, detrended = detrend(value, **kwargs)
    seasonal = seasonal_series(detrended, timestamp)
    anomalies = anomalies_series(value, seasonal)
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
