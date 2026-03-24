import pandas as pd
import statsmodels.api as sm


def lm_trend(timestamp: pd.Series, value: pd.Series, robust: bool = True) -> pd.Series:
    exog = sm.add_constant(timestamp)
    model = sm.RLM(value, exog, M=sm.robust.norms.HuberT() if robust else None)
    results = model.fit()

    return pd.Series(results.predict(exog), index=value.index, name="trend")


def ma_trend(value: pd.Series, window: int = 7) -> pd.Series:
    return value.rolling(window, min_periods=1, center=True).mean()
