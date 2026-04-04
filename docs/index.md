---
hide:
  - navigation
  - toc
---

# colombia-hydrodata

**Fetch hydrological and meteorological station data from Colombia in a single line of Python.**

`colombia-hydrodata` is a Python library that provides a clean, unified
interface to two official Colombian data sources: the
[IDEAM station catalog](https://www.datos.gov.co/) (Datos Abiertos Colombia)
and the [Aquarius WebPortal](https://aquarius.ideam.gov.co/). Query stations,
pull time-series datasets, and start analyzing water and climate data without
wrestling with raw APIs.

---

## Install

=== "pip"

    ```bash
    pip install colombia-hydrodata
    ```

=== "poetry"

    ```bash
    poetry add colombia-hydrodata
    ```

---

## Quick look

[![Open fetch-data in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sebnarvaez19/colombia-hydrodata/blob/main/docs/notebooks/fetch-data.ipynb)
[![Open plot-data in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sebnarvaez19/colombia-hydrodata/blob/main/docs/notebooks/plot-data.ipynb)

```python
from colombia_hydrodata import Client

client = Client()

# Fetch a station by its official IDEAM code
station = client.fetch_station("29037020")
print(station.name)
# CALAMAR

# Pull a daily mean streamflow dataset
dataset = station["CAUDAL@HIS_Q_MEDIA_D"]
print(dataset.data.head())
#              timestamp    value
# 0  2000-01-01 05:00:00  1240.80
# 1  2000-01-02 05:00:00  1179.00
# 2  2000-01-03 05:00:00  1143.40

# Built-in plotting helpers are available on dataset.plot
dataset.plot.time_series(title=station.name)
```

---

## Where to go next

<div class="grid cards" markdown>

- :material-rocket-launch-outline: **Getting Started**

  ***

  Install the library and run your first query in minutes.

  [:octicons-arrow-right-24: Getting Started](getting-started.md)

- :material-chart-line: **Plotting Tutorial**

  ***

  Learn how to use `dataset.plot`, `time_series_analysis()`, and
  `daily_series_analysis()`.

  [:octicons-arrow-right-24: Plotting](tutorial/plotting.md)

- :material-google-classroom: **Colab Notebooks**

  ***

  Run the fetch and plotting examples directly in Google Colab.

  [:octicons-arrow-right-24: Fetch Data](https://colab.research.google.com/github/sebnarvaez19/colombia-hydrodata/blob/main/docs/notebooks/fetch-data.ipynb)
  [:octicons-arrow-right-24: Plot Data](https://colab.research.google.com/github/sebnarvaez19/colombia-hydrodata/blob/main/docs/notebooks/plot-data.ipynb)

- :material-book-open-page-variant-outline: **API Reference**

  ***

  Full documentation for `Client`, `Station`, `Dataset`, `DatasetPlot`,
  `Filters`, `Location`, `Hydrographic`, and `Variable`.

  [:octicons-arrow-right-24: Reference](reference/client.md)

</div>
