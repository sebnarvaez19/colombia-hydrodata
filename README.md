# Colombia Hydrodata

[![PyPI](https://img.shields.io/pypi/v/colombia-hydrodata)](https://pypi.org/project/colombia-hydrodata/)
[![Docs](https://img.shields.io/badge/docs-online-teal)](https://sebnarvaez19.github.io/colombia-hydrodata/)

Python client for accessing hydrological and meteorological data from Colombia.

The library integrates official IDEAM data sources and exposes them through a
clean, Pythonic API for station discovery, dataset retrieval, and built-in
time-series plotting.

Data is fetched from:

- [Catalogo Nacional de Estaciones - Datos Abiertos Colombia](https://datos.gov.co/Ambiente-y-Desarrollo-Sostenible/Cat-logo-Nacional-de-Estaciones-del-IDEAM/hp9r-jxuu)
- [AQUARIUS WebPortal - IDEAM](http://aquariuswebportal.ideam.gov.co/)

---

## Architecture

The library follows a `client -> station -> dataset` hierarchy.

```text
Client
  └── Station
        └── Dataset
```

- `Client` loads the station catalog and exposes methods to query and filter stations.
- `Station` represents an IDEAM monitoring station with its full metadata and available variables.
- `Dataset` represents a time series retrieved from the Aquarius WebPortal.

---

## Installation

```bash
pip install colombia-hydrodata
```

Or with Poetry:

```bash
poetry add colombia-hydrodata
```

---

## Quick Start

```python
from colombia_hydrodata import Client

client = Client()

# Fetch a single station
station = client.fetch_station("29037020")
print(station.name)

# Fetch its discharge time series
dataset = station["CAUDAL@HIS_Q_MEDIA_D"]
print(dataset.data.head())
```

---

## Plotting

Datasets expose built-in plotting helpers through the `plot` property.

```python
import matplotlib.pyplot as plt

dataset.plot.time_series(title=station.name)
plt.show()
```

For decomposed series, you can generate the built-in analysis layouts:

```python
dataset = (
    station["NIVEL@NV_MEDIA_D"]
    .sight_level(-0.367)
    .rescale(1 / 100)
    .interpolate()
    .deconstruction()
)

fig, axs = dataset.plot.time_series_analysis(figsize=(10, 6), tight_layout=True)
plt.show()
```

You can also inspect the annual envelope and highlight specific years:

```python
fig, axs = dataset.plot.daily_series_analysis(
    years=[2024, 2025],
    figsize=(10, 4),
    tight_layout=True,
)
axs[0].legend()
plt.show()
```

---

## Client

`Client` is the main entry point. On initialization it downloads the full
IDEAM station catalog from Datos Abiertos Colombia and stores it internally as
a `GeoDataFrame`.

```python
from colombia_hydrodata import Client

client = Client()
```

---

## Fetching Stations

### Single station

```python
station = client.fetch_station("29037020")
```

Returns a `Station` object with full metadata.

### Multiple stations by ID

```python
stations = client.fetch_stations(["29037020", "29037021"])
```

Returns a list of `Station` objects.

---

## Spatial Queries

### Bounding box

```python
stations = client.fetch_bbox(
    xmin=-75.0,
    ymin=9.5,
    xmax=-74.0,
    ymax=10.5,
)
```

### Shapely geometry

```python
from shapely.geometry import Polygon

region = Polygon(...)
stations = client.fetch_region(region)
```

### Catalog only

To get a lightweight GeoDataFrame of station metadata without instantiating
`Station` objects:

```python
gdf = client.stations_in_region(region)
gdf = client.stations_in_list(["29037020", "29037021"])
```

---

## Filtering Stations

Use the `Filters` dataclass to narrow results by metadata fields. All filters
are optional and combined with logical `AND`.

```python
from colombia_hydrodata import Client
from colombia_hydrodata.filters import Filters

client = Client()

filters = Filters(
    category="Limnimetrica",
    department="Bolivar",
    status="Activa",
)

stations = client.fetch_region(region, filters=filters)
```

Available filter fields:

| Field                  | Description          |
| ---------------------- | -------------------- |
| `category`             | Station category     |
| `department`           | Department           |
| `municipality`         | Municipality         |
| `status`               | Operational status   |
| `owner`                | Owning institution   |
| `hydrographic_area`    | Hydrographic area    |
| `hydrographic_zone`    | Hydrographic zone    |
| `hydrographic_subzone` | Hydrographic subzone |

---

## Station

A `Station` is a frozen dataclass with full metadata about an IDEAM monitoring
station.

```python
station = client.fetch_station("29037020")
print(station)
```

It also provides the dataset access points:

```python
dataset = station.fetch("CAUDAL@HIS_Q_MEDIA_D")
dataset = station["CAUDAL@HIS_Q_MEDIA_D"]
```

Both return a `Dataset` object.

---

## Dataset

A `Dataset` represents a time series associated with a station and a variable.

```python
dataset = station["NIVEL@NV_MEDIA_D"]

print(dataset.station)
print(dataset.variable)
print(dataset.data.head())
```

The `data` DataFrame has two core columns:

| Column      | Description         |
| ----------- | ------------------- |
| `timestamp` | Datetime            |
| `value`     | Numeric measurement |

Datasets also expose transformation helpers such as:

- `sight_level()`
- `rescale()`
- `interpolate()`
- `detrend()`
- `seasonal()`
- `anomalies()`
- `deconstruction()`

And plotting helpers through:

```python
dataset.plot
```

---

## Documentation

Full documentation is available at:

https://sebnarvaez19.github.io/colombia-hydrodata/
