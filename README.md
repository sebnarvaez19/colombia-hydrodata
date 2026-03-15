# Colombia Hydrodata
(README.md made with ChatGPT).


Python client to access **hydrological and meteorological data from Colombia**.

The library integrates multiple official data sources and exposes them through a simple and Pythonic API.

Data is mainly fetched from:

* [Datos Abiertos Colombia](https://datos.gov.co/)
* [AQUARIUS WebPortal](http://aquariuswebportal.ideam.gov.co/)

---

# Architecture Overview

The library follows a **client–resource architecture**.

```
HydroClient
    ↓
Station
    ↓
Dataset
```

* **HydroClient** handles HTTP communication and catalog management.
* **Station** represents an IDEAM monitoring station and its metadata.
* **Dataset** represents a time series retrieved from Aquarius.

---

# Features

## HydroClient

`HydroClient` is the **main entry point** of the library.

It loads the **IDEAM station catalog** and exposes methods to query stations and retrieve datasets.

```python
from colombia_hydrodata import HydroClient

client = HydroClient()
```

When the client is initialized:

1. The **station catalog** is loaded from Datos Abiertos Colombia.
2. The catalog is cached locally to avoid repeated downloads.
3. The catalog is stored internally as a **pandas DataFrame**.

---

# Station Catalog

Station metadata comes from the IDEAM dataset:

**Catálogo Nacional de Estaciones IDEAM**

Source:

[https://datos.gov.co/Ambiente-y-Desarrollo-Sostenible/Cat-logo-Nacional-de-Estaciones-del-IDEAM/hp9r-jxuu](https://datos.gov.co/Ambiente-y-Desarrollo-Sostenible/Cat-logo-Nacional-de-Estaciones-del-IDEAM/hp9r-jxuu)

The catalog is downloaded through the **Socrata SODA API** using pagination.

---

# Disk Caching

The station catalog is cached locally to improve performance.

Caching uses the library:

```
platformdirs
```

Cache location (OS dependent):

| OS      | Cache Directory                            |
| ------- | ------------------------------------------ |
| Linux   | `~/.cache/colombia_hydrodata/`             |
| macOS   | `~/Library/Caches/colombia_hydrodata/`     |
| Windows | `%LOCALAPPDATA%\colombia_hydrodata\Cache\` |

Cached file:

```
stations_catalog.parquet
```

Cache behavior:

* loaded automatically when the client starts
* refreshed if the cache expires
* can be refreshed manually

This avoids unnecessary API calls and makes the client **start almost instantly** after the first execution.

---

# Fetching Stations

## Fetch a single station

```python
station = client.fetch_station("29037020")
```

Returns a `Station` object.

---

## Fetch multiple stations

```python
stations = client.fetch_stations(["29037020", "29037021"])
```

Returns a list of `Station` objects.

---

# Spatial Queries

Stations can be queried spatially using bounding boxes or geometries.

---

## Fetch stations in bounding box

```python
stations = client.fetch_bbox(-74.25, -4.25, -73.5, -3.5)
```

Returns station objects with metadata.

---

## Fetch stations in region

```python
stations = client.fetch_region(geometry)
```

The geometry can be:

* shapely polygon
* GeoJSON geometry
* GeoPandas geometry

---

## Get station list only

To obtain metadata without loading datasets:

```python
stations = client.stations_in_region(geometry)
```

---

## Nearest station

Find the closest station to a given coordinate.

```python
station = client.fetch_nearest(lon, lat)
```

Distance is computed using station coordinates from the catalog.

---

# Station Filtering

Stations can be filtered using a dedicated **StationFilter** class.

```python
from colombia_hydrodata import HydroClient, StationFilter

client = HydroClient()

filters = StationFilter(type=["limnigraphic", "limnimetric"])

stations = client.fetch_region(polygon, filters=filters)
```

Filters are validated to avoid invalid parameters.

Possible filter fields include:

* station type
* department
* municipality
* variables
* operational state

Multiple filters are combined using logical **AND**, while lists represent **OR** conditions.

---

# Stations

`Station` objects represent IDEAM monitoring stations.

Stations are implemented as **dataclasses with read-only attributes**.

A station contains metadata and information about available variables.

```
Station
  id
  name
  type
  technology
  state
  department
  municipality
  altitude
  longitude
  latitude
  installation_date
  suspension_date
  operative_area
  river
  AH   (Hydrographic Area)
  ZH   (Hydrographic Zone)
  SZH  (Hydrographic Subzone)
  entity
```

Stations also list the variables measured by the station and the time frequencies available.

Example:

```
variables:
  rainfall: ["D", "M", "A"]
  stage: ["H", "D", "M", "A"]
  discharge: ["H", "D", "M", "A"]
```

---

# Fetching Data

Datasets are retrieved from the **Aquarius WebPortal**.

Each variable and frequency corresponds to an Aquarius dataset.

Example:

```python
dataset = station.fetch("stage", "H")
```

This process:

1. identifies the Aquarius dataset
2. retrieves the time series
3. returns a `Dataset` object

---

# Dataset

A `Dataset` represents a **time series associated with a station**.

Internally, the data is stored as a **pandas DataFrame**.

Example structure:

```
Dataset
  station
  variable
  frequency
  data
```

Example dataframe:

| timestamp  | value |
| ---------- | ----- |
| 2025-01-01 | 2.31  |
| 2025-01-02 | 2.28  |

---

# Dataset Operations

Datasets include utilities for analysis and export.

### Plot time series

```python
dataset.plot()
```

---

### Export data

```python
dataset.to_csv()
dataset.to_parquet()
```

---

### Convert to spatial data

```python
dataset.to_geodataframe()
```

Returns a **GeoDataFrame** with station geometry.

---

# Stage (River Level) Data

The variable **stage** represents the water level relative to the gauge reference.

In Colombian hydrology it is common to convert stage to **absolute water elevation** using the **station sight level (cota de mira)**.

---

# Sight Level Correction

Users can apply sight level corrections when fetching stage data.

## Constant sight level

```python
dataset = station.fetch(
    "stage",
    "H",
    sight_level=124.80
)
```

Elevation is computed as:

```
elevation = stage + sight_level
```

---

## Time-varying sight levels

Stations sometimes change gauge reference.

Users can define time-dependent corrections.

```python
dataset = station.fetch(
    "stage",
    "H",
    sight_level=[
        ("2000-01-01", 124.80),
        ("2015-06-01", 125.10)
    ]
)
```

---

## Apply correction after fetching

```python
dataset.apply_sight_level(124.8)
```

or

```python
dataset.apply_sight_level([
    ("2000-01-01", 124.8),
    ("2015-01-01", 125.1)
])
```

---

# Mapping Stations

Stations can be visualized spatially.

```python
client.map_stations(stations)
```

This creates a map showing station locations.

---

# Dependencies

Core dependencies:

```
requests
pandasHere is the **updated and consolidated design sheet**, integrating everything we discussed today:

* `HydroClient` architecture
* `Station` and `Dataset` dataclasses
* `StationFilter`
* spatial queries
* Aquarius data fetching
* stage **sight level correction**
* **disk caching using `platformdirs`**
* station catalog from **datos.gov.co**

I kept the tone **documentation-friendly** so this can become your **README.md** or **design.md** directly.

---

# Colombia Hydrodata

Python client to access **hydrological and meteorological data from Colombia**.

The library integrates multiple official data sources and exposes them through a simple and Pythonic API.

Data is mainly fetched from:

* Instituto de Hidrología, Meteorología y Estudios Ambientales (IDEAM)
* Datos Abiertos Colombia
* Aquarius WebPortal

---

# Architecture Overview

The library follows a **client–resource architecture**.

```
HydroClient
    ↓
Station
    ↓
Dataset
```

* **HydroClient** handles HTTP communication and catalog management.
* **Station** represents an IDEAM monitoring station and its metadata.
* **Dataset** represents a time series retrieved from Aquarius.

---

# Features

## HydroClient

`HydroClient` is the **main entry point** of the library.

It loads the **IDEAM station catalog** and exposes methods to query stations and retrieve datasets.

```python
from colombia_hydrodata import HydroClient

client = HydroClient()
```

When the client is initialized:

1. The **station catalog** is loaded from Datos Abiertos Colombia.
2. The catalog is cached locally to avoid repeated downloads.
3. The catalog is stored internally as a **pandas DataFrame**.

---

# Station Catalog

Station metadata comes from the IDEAM dataset:

**Catálogo Nacional de Estaciones IDEAM**

Source:

[https://datos.gov.co/Ambiente-y-Desarrollo-Sostenible/Cat-logo-Nacional-de-Estaciones-del-IDEAM/hp9r-jxuu](https://datos.gov.co/Ambiente-y-Desarrollo-Sostenible/Cat-logo-Nacional-de-Estaciones-del-IDEAM/hp9r-jxuu)

The catalog is downloaded through the **Socrata SODA API** using pagination.

---

# Disk Caching

The station catalog is cached locally to improve performance.

Caching uses the library:

```
platformdirs
```

Cache location (OS dependent):

| OS      | Cache Directory                            |
| ------- | ------------------------------------------ |
| Linux   | `~/.cache/colombia_hydrodata/`             |
| macOS   | `~/Library/Caches/colombia_hydrodata/`     |
| Windows | `%LOCALAPPDATA%\colombia_hydrodata\Cache\` |

Cached file:

```
stations_catalog.parquet
```

Cache behavior:

* loaded automatically when the client starts
* refreshed if the cache expires
* can be refreshed manually

This avoids unnecessary API calls and makes the client **start almost instantly** after the first execution.

---

# Fetching Stations

## Fetch a single station

```python
station = client.fetch_station("29037020")
```

Returns a `Station` object.

---

## Fetch multiple stations

```python
stations = client.fetch_stations(["29037020", "29037021"])
```

Returns a list of `Station` objects.

---

# Spatial Queries

Stations can be queried spatially using bounding boxes or geometries.

---

## Fetch stations in bounding box

```python
stations = client.fetch_bbox(-74.25, -4.25, -73.5, -3.5)
```

Returns station objects with metadata.

---

## Fetch stations in region

```python
stations = client.fetch_region(geometry)
```

The geometry can be:

* shapely polygon
* GeoJSON geometry
* GeoPandas geometry

---

## Get station list only

To obtain metadata without loading datasets:

```python
stations = client.stations_in_region(geometry)
```

---

## Nearest station

Find the closest station to a given coordinate.

```python
station = client.fetch_nearest(lon, lat)
```

Distance is computed using station coordinates from the catalog.

---

# Station Filtering

Stations can be filtered using a dedicated **StationFilter** class.

```python
from colombia_hydrodata import HydroClient, StationFilter

client = HydroClient()

filters = StationFilter(type=["limnigraphic", "limnimetric"])

stations = client.fetch_region(polygon, filters=filters)
```

Filters are validated to avoid invalid parameters.

Possible filter fields include:

* station type
* department
* municipality
* variables
* operational state

Multiple filters are combined using logical **AND**, while lists represent **OR** conditions.

---

# Stations

`Station` objects represent IDEAM monitoring stations.

Stations are implemented as **dataclasses with read-only attributes**.

A station contains metadata and information about available variables.

```
Station
  id
  name
  type
  technology
  state
  department
  municipality
  altitude
  longitude
  latitude
  installation_date
  suspension_date
  operative_area
  river
  AH   (Hydrographic Area)
  ZH   (Hydrographic Zone)
  SZH  (Hydrographic Subzone)
  entity
```

Stations also list the variables measured by the station and the time frequencies available.

Example:

```
variables:
  rainfall: ["D", "M", "A"]
  stage: ["H", "D", "M", "A"]
  discharge: ["H", "D", "M", "A"]
```

---

# Fetching Data

Datasets are retrieved from the **Aquarius WebPortal**.

Each variable and frequency corresponds to an Aquarius dataset.

Example:

```python
dataset = station.fetch("stage", "H")
```

This process:

1. identifies the Aquarius dataset
2. retrieves the time series
3. returns a `Dataset` object

---

# Dataset

A `Dataset` represents a **time series associated with a station**.

Internally, the data is stored as a **pandas DataFrame**.

Example structure:

```
Dataset
  station
  variable
  frequency
  data
```

Example dataframe:

| timestamp  | value |
| ---------- | ----- |
| 2025-01-01 | 2.31  |
| 2025-01-02 | 2.28  |

---

# Dataset Operations

Datasets include utilities for analysis and export.

### Plot time series

```python
dataset.plot()
```

---

### Export data

```python
dataset.to_csv()
dataset.to_parquet()
```

---

### Convert to spatial data

```python
dataset.to_geodataframe()
```

Returns a **GeoDataFrame** with station geometry.

---

# Stage (River Level) Data

The variable **stage** represents the water level relative to the gauge reference.

In Colombian hydrology it is common to convert stage to **absolute water elevation** using the **station sight level (cota de mira)**.

---

# Sight Level Correction

Users can apply sight level corrections when fetching stage data.

## Constant sight level

```python
dataset = station.fetch(
    "stage",
    "H",
    sight_level=124.80
)
```

Elevation is computed as:

```
elevation = stage + sight_level
```

---

## Time-varying sight levels

Stations sometimes change gauge reference.

Users can define time-dependent corrections.

```python
dataset = station.fetch(
    "stage",
    "H",
    sight_level=[
        ("2000-01-01", 124.80),
        ("2015-06-01", 125.10)
    ]
)
```

---

## Apply correction after fetching

```python
dataset.apply_sight_level(124.8)
```

or

```python
dataset.apply_sight_level([
    ("2000-01-01", 124.8),
    ("2015-01-01", 125.1)
])
```

---

# Mapping Stations

Stations can be visualized spatially.

```python
client.map_stations(stations)
```

This creates a map showing station locations.

---

# Dependencies

Core dependencies:

```
requests
pandas
aquarius_webportal
platformdirs
```

Optional spatial dependencies:

```
geopandas
shapely
folium
```

---

# Example Workflow

```python
from colombia_hydrodata import HydroClient

client = HydroClient()

station = client.fetch_station("29037020")

dataset = station.fetch("stage", "H", sight_level=124.8)

dataset.plot()
```
