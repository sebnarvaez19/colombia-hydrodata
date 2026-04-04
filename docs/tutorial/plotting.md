# Plotting

This tutorial shows how to use the `dataset.plot` interface to generate the
built-in visual diagnostics provided by `colombia-hydrodata`.

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sebnarvaez19/colombia-hydrodata/blob/main/docs/notebooks/plot-data.ipynb)

---

## Prepare a dataset

The plotting helpers are most useful after interpolation and time-series
decomposition, because several plots rely on `trend`, `detrended`, and
`anomalies` columns.

```python
from colombia_hydrodata import Client
import matplotlib.pyplot as plt

client = Client()
station = client.fetch_station("29037020")

dataset = (
    station["NIVEL@NV_MEDIA_D"]
    .sight_level(-0.367)
    .rescale(1 / 100)
    .interpolate()
    .deconstruction()
)
```

Once you have a dataset, the plotting API is available through `dataset.plot`.

---

## Basic plots

```python
dataset.plot.time_series()
dataset.plot.histogram(column_name="detrended", bins=40)
dataset.plot.monthly_data_series(column_name="detrended")
plt.show()
```

These methods return Matplotlib `Axes`, so you can continue styling them:

```python
ax = dataset.plot.time_series()
ax.set(title=station.name, ylabel="Water level [m]")
plt.show()
```

---

## Time-series analysis

`time_series_analysis()` generates a four-panel diagnostic figure. The default
layout is the compact dashboard view:

```python
fig, axs = dataset.plot.time_series_analysis(
    figsize=(10, 6),
    tight_layout=True,
)
plt.show()
```

This view includes:

- The original time series
- A histogram of the detrended series
- The anomalies stem plot
- The monthly seasonal pattern

If you prefer a stacked layout, use `layout="classic"`:

```python
fig, axs = dataset.plot.time_series_analysis(
    layout="classic",
    figsize=(10, 8),
    tight_layout=True,
)
plt.show()
```

---

## Daily series analysis

`daily_series_analysis()` focuses on the annual cycle. It combines the annual
envelope with a histogram and can highlight specific years on top of the
historical range.

```python
fig, axs = dataset.plot.daily_series_analysis(
    years=[2024, 2025],
    figsize=(10, 4),
    tight_layout=True,
)
axs[0].legend()
plt.show()
```

This is useful when you want to compare recent years with the long-term annual
distribution for the same station and variable.

---

## Working directly with Matplotlib

The plotting helpers always return Matplotlib objects, so you can integrate
them into your own figure layouts:

```python
fig, axs = plt.subplots(1, 2, figsize=(12, 4), tight_layout=True)

dataset.plot.monthly_data_series(column_name="detrended", ax=axs[0])
axs[0].set(title="Seasonal pattern")

dataset.plot.annual_data_series(years=[2025], ax=axs[1])
axs[1].legend()
axs[1].set(title="Annual envelope")

plt.show()
```

---

## What's next?

See the API reference for full method signatures and available parameters.

[:octicons-arrow-right-24: Plot Reference](../reference/plot.md)
