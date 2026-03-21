# Stations

A `Station` is an immutable snapshot of everything IDEAM records about a
monitoring site — coordinates, administrative classification, hydrographic
context, and the full list of measurement variables available in the Aquarius
WebPortal. Once you have a `Station` object you can inspect its metadata and
pull any of its time series with a single call.

---

## Fetching a single station

Pass an eight-digit IDEAM station code to `client.fetch_station()`:

```python
from colombia_hydrodata import Client

client = Client()
station = client.fetch_station("29037020")
```

!!! warning "Network call on every fetch"
Unlike reading rows from `client.catalog`, `fetch_station` always makes a
live request to the Aquarius WebPortal to discover all variables available
at that station. Budget a few seconds per call.

---

## Printing a station

`Station` ships with a `__str__` that gives you a readable overview of every
field at a glance:

```python
print(station)
```

```text
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

Variables are grouped by their parameter prefix (`CAUDAL`, `NIVEL`, …) so you
can quickly see what a station measures before deciding which series to fetch.

---

## Accessing station attributes

`Station` is a [frozen dataclass](https://docs.python.org/3/library/dataclasses.html#frozen-instances)
— all fields are set once at construction time and are read-only thereafter.

### Scalar fields

```python
print(station.id)           # "29037020"
print(station.name)         # "CALAMAR"
print(station.category)     # "Limnimétrica"
print(station.technology)   # "Convencional"
print(station.status)       # "Activa"
print(station.department)   # "BOLIVAR"
print(station.municipality) # "CALAMAR"
print(station.owner)        # "INSTITUTO DE HIDROLOGÍA METEOROLOGÍA Y ESTUDIOS AMBIENTALES"
```

### Dates

```python
print(station.installation_date)  # 1940-07-15 00:00:00
print(station.suspension_date)    # NaT  ← station is still active
```

!!! info "Suspended stations"
When `suspension_date` is not `NaT`, the station is no longer collecting
data. The `status` field will read `"Suspendida"` in those cases.

### `location`

`station.location` is a `Location` dataclass with three fields:

```python
loc = station.location

print(loc.latitude)   # 10.243
print(loc.longitude)  # -74.915
print(loc.altitude)   # 8.0

print(loc)  # Location: altitude=8.00 [-74.915; 10.243]
```

### `hydrographic`

`station.hydrographic` is a `Hydrographic` dataclass that places the station
within Colombia's official hydrographic hierarchy:

```python
hydro = station.hydrographic

print(hydro.hydrographic_area)    # "Magdalena Cauca"
print(hydro.hydrographic_zone)    # "Bajo Magdalena"
print(hydro.hydrographic_subzone) # "Canal del Dique margen izquierda"

print(hydro)
# Hydrographic: area=Magdalena Cauca zone=Bajo Magdalena
#               subzone=Canal del Dique margen izquierda
```

### `variables`

`station.variables` is a `dict[str, Variable]` whose keys follow the
`PARAM@LABEL` convention:

```python
for key, var in station.variables.items():
    print(f"{key:30s}  id={var.id}")
```

```text
CAUDAL@HIS_Q_MEDIA_D            id=...
CAUDAL@HIS_Q_MX_M               id=...
CAUDAL@Q_MN_D                   id=...
CAUDAL@Q_MX_D                   id=...
NIVEL@NV_MEDIA_D                id=...
NIVEL@NV_MX_D                   id=...
NIVEL@HIS_NV_MEDIA_D            id=...
TM@HIS_TR_QS_M                  id=...
```

Each `Variable` value exposes three attributes:

| Attribute | Type  | Example                     |
| --------- | ----- | --------------------------- |
| `param`   | `str` | `"CAUDAL"`                  |
| `label`   | `str` | `"HIS_Q_MEDIA_D"`           |
| `id`      | `int` | numeric Aquarius dataset ID |

---

## Checking variable availability

Use the `in` operator to test whether a key is present before fetching, which
avoids an unnecessary network request on a miss:

```python
if "CAUDAL@HIS_Q_MEDIA_D" in station:
    print("Daily mean streamflow is available")

if "PRECIPITACION@PP_DIARIA" not in station:
    print("Rainfall is not recorded at this station")
```

!!! note "Keys are case-insensitive"
Variable keys are normalised to upper-case internally, so both
`"CAUDAL@HIS_Q_MEDIA_D"` and `"caudal@his_q_media_d"` work correctly.

To see every available key at once:

```python
print(list(station.variables.keys()))
```

```text
['CAUDAL@HIS_Q_MEDIA_D', 'CAUDAL@HIS_Q_MAX_D', 'CAUDAL@HIS_Q_MIN_D',
 'NIVEL@NV_MEDIA_D', 'NIVEL@NV_MAX_D', 'NIVEL@NV_MIN_D']
```

---

## Fetching a dataset

Once you know which variable you need, retrieve its full time series with
either `fetch()` or bracket notation — they are completely equivalent:

=== "fetch()"

    ```python
    dataset = station.fetch("CAUDAL@HIS_Q_MEDIA_D")
    ```

=== "Bracket notation"

    ```python
    dataset = station["CAUDAL@HIS_Q_MEDIA_D"]
    ```

Both return a [`Dataset`](datasets.md) containing a pandas `DataFrame` ready
for analysis.

!!! warning "Error conditions"
Two exceptions can be raised when fetching a dataset:

    - **`TypeError`** — the station has no variables at all (rare, but
      possible for very old suspended stations).
    - **`KeyError`** — the requested key was not found. The error message
      lists every available key to help you correct the typo.

    Always guard with `in` first if you are iterating over many stations
    whose variable availability is unknown.

### Fetching multiple variables at once

Combine `fetch()` calls for the same station without re-fetching station
metadata — the `Station` object is reused across all calls:

```python
mean_flow = station["CAUDAL@HIS_Q_MEDIA_D"]
max_flow  = station["CAUDAL@HIS_Q_MAX_D"]
min_flow  = station["CAUDAL@HIS_Q_MIN_D"]

import pandas as pd

summary = pd.DataFrame({
    "mean": mean_flow.data.set_index("timestamp")["value"],
    "max":  max_flow.data.set_index("timestamp")["value"],
    "min":  min_flow.data.set_index("timestamp")["value"],
})

print(summary.tail(3))
```

```text
                          mean     max     min
timestamp
2023-12-29 05:00:00   1821.3  2104.5  1612.8
2023-12-30 05:00:00   1793.6  2078.1  1581.2
2023-12-31 05:00:00   1748.9  2031.4  1540.7
```

---

## What's next?

Learn how to work with the time-series data inside a `Dataset`, including
filtering by date, computing statistics, and exporting to CSV.

[:octicons-arrow-right-24: Working with Datasets](datasets.md)
