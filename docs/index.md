---
hide:
  - navigation
  - toc
---

# colombia-hydrodata

**Fetch hydrological and meteorological station data from Colombia — in a single line of Python.**

`colombia-hydrodata` is a Python library that provides a clean, unified interface to two official Colombian data sources: the [IDEAM station catalog](https://www.datos.gov.co/) (Datos Abiertos Colombia) and the [Aquarius WebPortal](https://aquarius.ideam.gov.co/). Query stations, pull time-series datasets, and start analysing water and climate data without wrestling with raw APIs.

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
```

---

## Where to go next

<div class="grid cards" markdown>

- :material-rocket-launch-outline: **Getting Started**

  ***

  Install the library and run your first query in minutes.

  [:octicons-arrow-right-24: Getting Started](getting-started.md)

- :material-book-open-page-variant-outline: **API Reference**

  ***

  Full documentation for `Client`, `Station`, `Dataset`, `Filters`, `Location`, `Hydrographic`, and `Variable`.

  [:octicons-arrow-right-24: Reference](reference/client.md)

</div>
