# Colombia Hydrodata

Python client to access **hydrological and meteorological data from Colombia**.

The library integrates multiple official data sources and exposes them through a simple and Pythonic API.

Data is fetched from:

- [Catálogo Nacional de Estaciones – Datos Abiertos Colombia](https://datos.gov.co/Ambiente-y-Desarrollo-Sostenible/Cat-logo-Nacional-de-Estaciones-del-IDEAM/hp9r-jxuu)
- [AQUARIUS WebPortal – IDEAM](http://aquariuswebportal.ideam.gov.co/)

---

## Architecture

The library follows a **client → station → dataset** hierarchy.

```
Client
  └── Station
        └── Dataset
```

- **`Client`** loads the station catalog and exposes methods to query and filter stations.
- **`Station`** represents an IDEAM monitoring station with its full metadata and available variables.
- **`Dataset`** represents a time series retrieved from the Aquarius WebPortal.

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
from colombia_hydrodata.client import Client

client = Client()

# Fetch a single station
station = client.fetch_station("29037020")
print(station)

# Fetch its discharge time series
dataset = station["CAUDAL@HIS_Q_MEDIA_D"]
print(dataset.data)
```

---

## Client

`Client` is the main entry point. On initialization it downloads the full IDEAM station catalog from Datos Abiertos Colombia and stores it internally as a **GeoDataFrame**.

```python
from colombia_hydrodata.client import Client

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
    ymax=10.5
)
```

### Shapely geometry

```python
from shapely.geometry import Polygon

region = Polygon(...)
stations = client.fetch_region(region)
```

### Catalog only (no Station objects)

To get a lightweight GeoDataFrame of station metadata without instantiating `Station` objects:

```python
gdf = client.stations_in_region(region)
gdf = client.stations_in_list(["29037020", "29037021"])
```

---

## Filtering Stations

Use the `Filters` dataclass to narrow results by metadata fields. All filters are combined with logical **AND** and are optional.

```python
from colombia_hydrodata.client import Client
from colombia_hydrodata.filters import Filters

client = Client()

filters = Filters(
    category="Limnimétrica",
    department="Bolivar",
    status="Activa",
)

stations = client.fetch_region(region, filters=filters)
```

Available filter fields:

| Field                  | Description              |
|------------------------|--------------------------|
| `category`             | Station category         |
| `department`           | Department               |
| `municipality`         | Municipality             |
| `status`               | Operational status       |
| `owner`                | Owning institution       |
| `hydrographic_area`    | Hydrographic area        |
| `hydrographic_zone`    | Hydrographic zone        |
| `hydrographic_subzone` | Hydrographic subzone     |

---

## Station

A `Station` is a **frozen dataclass** (read-only) with full metadata about an IDEAM monitoring station.

```python
station = client.fetch_station("29037020")
print(station)
```

Example output:

```
Station CALAMAR: 29037020
  Calamar (Bolivar)
  Info: Activa Limnimétrica (Convencional)
  Time: 1940-07-15 00:00:00 - ongoing
  Owner: INSTITUTO DE HIDROLOGÍA METEOROLOGÍA Y ESTUDIOS AMBIENTALES
  Location: altitude=8.00 [-74.915; 10.243]
  Hydrographic: area=Magdalena Cauca zone=Bajo Magdalena subzone=Canal del Dique margen izquierda
  Variables:
    CAUDAL:
       HIS_Q_MEDIA_D, HIS_Q_MX_M, HIS_Q_MEDIA_M, Q_MN_D, Q_MN_M, Q_MX_D, Q_MX_M, Q_MN_A, Q_MX_A, Q_MEDIA_A, CAUDAL_H
    NIVEL:
       NVLM_CON, HIS_NV_MEDIA_D, HIS_NV_MN_M, HIS_NV_MX_M, NIVEL_H, NV_MEDIA_D, NV_MN_D, NV_MN_M, NV_MX_D, NV_MX_M, NV_MN_A, NV_MX_A, NV_MEDIA_A, HIS_NIVEL_H
    TM:
       HIS_TR_QS_M, HIS_TR_QS_TT_M, HIS_TR_QS_MX_M, HIS_TR_KT/D_QS_D
```

### Station attributes

| Attribute           | Description                        |
|---------------------|------------------------------------|
| `id`                | Station code                       |
| `name`              | Station name                       |
| `category`          | Category (e.g. Limnimétrica)       |
| `technology`        | Technology (e.g. Convencional)     |
| `status`            | Operational status                 |
| `department`        | Department                         |
| `municipality`      | Municipality                       |
| `installation_date` | Date the station was installed     |
| `suspension_date`   | Date suspended (`None` if active)  |
| `owner`             | Owning institution                 |
| `location`          | `Location` (altitude, lon, lat)    |
| `hydrographic`      | `Hydrographic` (area, zone, subzone)|
| `variables`         | Dict of available `Variable` objects|

### Checking variable availability

```python
"CAUDAL@HIS_Q_MEDIA_D" in station  # True / False
```

---

## Fetching Data

Variables are identified by a key in the format `PARAM@LABEL`, matching the variables listed when you print a station.

### Using `fetch()`

```python
dataset = station.fetch("CAUDAL@HIS_Q_MEDIA_D")
```

### Using `[]` (shorthand)

```python
dataset = station["CAUDAL@HIS_Q_MEDIA_D"]
```

Both return a `Dataset` object.

---

## Dataset

A `Dataset` represents a **time series associated with a station and a variable**.

```python
dataset = station["NIVEL@NV_MEDIA_D"]

print(dataset.station)    # Station object
print(dataset.variable)   # Variable object (param, label, id)
print(dataset.data)       # pandas DataFrame
```

The `data` DataFrame has two columns:

| Column      | Description         |
|-------------|---------------------|
| `timestamp` | datetime            |
| `value`     | numeric measurement |

Example:

```
   timestamp   value
0  2025-01-01   2.31
1  2025-01-02   2.28
2  2025-01-03   2.35
```

---

## Data Sources

### Station Catalog

Fetched from the **Socrata SODA API** via Datos Abiertos Colombia:

```
https://datos.gov.co/resource/hp9r-jxuu.json
```

### Time Series

Fetched from the **IDEAM Aquarius WebPortal**:

```
http://aquariuswebportal.ideam.gov.co/
```

Each variable key (`PARAM@LABEL`) corresponds to a unique Aquarius dataset ID used internally to retrieve the time series.

---

*README made with [GitHub Copilot](https://github.com/features/copilot).*

