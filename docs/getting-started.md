# Getting Started

This page walks you through installing `colombia-hydrodata` and running your
very first query against a real Colombian hydrological station.

---

## Requirements

!!! warning "Python version"
    `colombia-hydrodata` requires **Python 3.12 or newer**.
    Run `python --version` to confirm before installing.

| Dependency           | Minimum version | Notes                     |
| -------------------- | --------------- | ------------------------- |
| Python               | 3.12            | Required                  |
| `requests`           | 2.32            | HTTP transport            |
| `pandas`             | 3.0             | Returned datasets         |
| `geopandas`          | 1.1             | Catalog GeoDataFrame      |
| `shapely`            | 2.1             | Geometry objects          |
| `aquarius-webportal` | 0.4             | Aquarius WebPortal client |
| `pyarrow`            | 23.0            | Parquet catalog cache     |

---

## Installation

Choose your preferred package manager:

=== "pip"

    ```bash
    pip install colombia-hydrodata
    ```

    To pin an exact version in a `requirements.txt` file:

    ```text
    colombia-hydrodata==0.1.0
    ```

=== "poetry"

    ```bash
    poetry add colombia-hydrodata
    ```

    This will add the following entry to your `pyproject.toml`:

    ```toml
    [tool.poetry.dependencies]
    colombia-hydrodata = "^0.1.0"
    ```

!!! tip "Virtual environments"
    It is strongly recommended to install inside a virtual environment
    (`python -m venv .venv`) or a Poetry-managed shell (`poetry shell`) to
    avoid dependency conflicts.

---

## Your first query

The steps below retrieve station **29037020** (Calamar, Bolivar) and pull its
daily mean streamflow time series.

### Step 1 - Import `Client`

```python
from colombia_hydrodata import Client
```

`Client` is the single entry point to both data sources: the IDEAM station
catalog (Datos Abiertos Colombia) and the Aquarius WebPortal. You never need
to instantiate the underlying source adapters directly.

---

### Step 2 - Create a client

```python
client = Client()
```

`Client()` takes no arguments. On creation it fetches the full CNE station
catalog from datos.gov.co and stores it as a `GeoDataFrame` in
`client.catalog`. Both endpoints are fully public, so no API key is required.

---

### Step 3 - Fetch a station

```python
station = client.fetch_station("29037020")
print(station.name)
print(station.department)
print(station.location)
```

`fetch_station` looks up the station by its official IDEAM eight-digit code
and returns a frozen `Station` dataclass:

```text
CALAMAR
BOLIVAR
Location: altitude=8.00 [-74.915; 10.243]
```

!!! info "Available attributes"
    | Attribute | Type | Description |
    |---|---|---|
    | `station.id` | `str` | Official IDEAM station code |
    | `station.name` | `str` | Human-readable station name |
    | `station.category` | `str` | Station type (e.g. `"Limnigrafica"`) |
    | `station.status` | `str` | Operational status (`"Activa"` / `"Suspendida"`) |
    | `station.department` | `str` | Colombian department |
    | `station.municipality` | `str` | Municipality |
    | `station.owner` | `str` | Operating entity |
    | `station.location` | `Location` | Altitude, longitude, latitude |
    | `station.hydrographic` | `Hydrographic` | Hydrographic area, zone, and subzone |
    | `station.variables` | `dict[str, Variable]` | All available time-series variables |

---

### Step 4 - Fetch a dataset

Variable keys follow the pattern `PARAM@LABEL`. For daily mean streamflow the
key is `CAUDAL@HIS_Q_MEDIA_D`:

```python
dataset = station["CAUDAL@HIS_Q_MEDIA_D"]
# or equivalently:
dataset = station.fetch("CAUDAL@HIS_Q_MEDIA_D")
```

This queries the Aquarius WebPortal and returns a `Dataset` object backed by a
`pandas.DataFrame`.

---

### Step 5 - Inspect the data

```python
print(dataset.data.head())
```

`dataset.data` is a standard `pandas.DataFrame` with two columns:

```text
             timestamp    value
0  2000-01-01 05:00:00  1240.80
1  2000-01-02 05:00:00  1179.00
2  2000-01-03 05:00:00  1143.40
3  2000-01-04 05:00:00  1113.60
4  2000-01-05 05:00:00  1066.60
```

You can immediately use familiar pandas operations:

```python
# Monthly averages
monthly = dataset.data.set_index("timestamp")["value"].resample("ME").mean()

# Plot with the built-in helper
dataset.plot.time_series(title=station.name)
```

---

### Putting it all together

Here is the complete example as a single script:

```python
from colombia_hydrodata import Client

client = Client()

station = client.fetch_station("29037020")
print(station.name, station.department)
print(list(station.variables.keys()))

dataset = station["CAUDAL@HIS_Q_MEDIA_D"]

print(dataset.data.head())
print(f"Total records : {len(dataset.data)}")
print(f"Mean discharge: {dataset.data['value'].mean():.1f} m3/s")
```

---

## What's next

!!! success "You're ready!"
    You have successfully installed the library and pulled real hydrological
    data from Colombia.

<div class="grid cards" markdown>

- :material-book-education-outline: **Tutorial**

  ***

  A hands-on walkthrough: discover stations with `Filters`, work with
  datasets, and generate built-in plots.

  [:octicons-arrow-right-24: Tutorial](tutorial/client.md)

- :material-book-open-page-variant-outline: **API Reference**

  ***

  Detailed documentation for every public class: `Client`, `Station`,
  `Dataset`, `DatasetPlot`, `Filters`, `Location`, `Hydrographic`, and
  `Variable`.

  [:octicons-arrow-right-24: Reference](reference/client.md)

</div>
