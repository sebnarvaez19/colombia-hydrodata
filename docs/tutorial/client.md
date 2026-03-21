# The Client

The `Client` class is your single entry point into `colombia-hydrodata`. Creating one instance downloads the full IDEAM station catalog and exposes it as a `GeoDataFrame` that is ready for filtering, inspection, and spatial analysis — all before you fetch a single time series.

---

## Importing and creating a client

```python
from colombia_hydrodata import Client

client = Client()
```

That one line does everything needed to get started. On instantiation, `Client` sends a request to the Datos Abiertos Colombia CNE endpoint, parses and cleans the response, attaches a Shapely `Point` geometry to every row, and stores the result as `client.catalog`.

!!! tip "The catalog is cached locally"
    Repeated calls to `Client()` within the same week are near-instant.
    The catalog is persisted as a Parquet file in your platform's user-cache
    directory (`~/.cache/colombia-hydrodata/` on Linux and macOS, or the
    equivalent `%LOCALAPPDATA%\colombia-hydrodata\` on Windows) and is
    considered fresh for **7 days**. After that, the next instantiation
    re-downloads the catalog automatically.

---

## Inspecting the catalog

`client.catalog` is a standard `geopandas.GeoDataFrame`, so every pandas
and GeoPandas operation you already know works on it without any adaptation.

### Schema and memory usage

```python
client.catalog.info()
```

```text
<class 'geopandas.geodataframe.GeoDataFrame'>
RangeIndex: 4892 entries, 0 to 4891
Data columns (total 17 columns):
 #   Column                Non-Null Count  Dtype
---  ------                --------------  -----
 0   id                    4892 non-null   object
 1   name                  4892 non-null   object
 2   category              4892 non-null   object
 3   technology            4892 non-null   object
 4   status                4892 non-null   object
 5   department            4892 non-null   object
 6   municipality          4892 non-null   object
 7   altitude              4876 non-null   float64
 8   longitude             4892 non-null   float64
 9   latitude              4892 non-null   float64
 10  installation_date     4812 non-null   datetime64[ns]
 11  suspension_date       1342 non-null   datetime64[ns]
 12  hydrographic_area     4892 non-null   object
 13  hydrographic_zone     4892 non-null   object
 14  hydrographic_subzone  4892 non-null   object
 15  owner                 4892 non-null   object
 16  geometry              4892 non-null   geometry
dtypes: datetime64[ns](2), float64(3), geometry(1), object(11)
memory usage: 649.8 KB
```

### Previewing the first rows

```python
client.catalog[["id", "name", "category", "status", "department", "geometry"]].head(3)
```

| id | name | category | status | department | geometry |
|---|---|---|---|---|---|
| 21180010 | BETANIA - EMBALSE | Limnigráfica | Activa | HUILA | POINT (-75.524 2.641) |
| 21190010 | PESCADERO | Limnimétrica | Activa | HUILA | POINT (-75.178 2.898) |
| 21218010 | VILLAVIEJA | Climática | Activa | HUILA | POINT (-75.215 3.213) |

### Counting categories and statuses

```python
print(client.catalog["category"].value_counts())
```

```text
category
Climática        2104
Limnigráfica     1108
Limnimétrica      923
Pluviométrica     589
Pluviográfica     168
dtype: int64
```

```python
print(client.catalog["status"].value_counts())
```

```text
status
Activa        3412
Suspendida    1480
dtype: int64
```

---

## Filtering the catalog with pandas

Because `client.catalog` is a plain DataFrame under the hood, you can
filter it with any standard boolean indexing expression.

=== "By department and status"

    ```python
    antioquia_active = client.catalog[
        (client.catalog["department"] == "ANTIOQUIA") &
        (client.catalog["status"]     == "Activa")
    ]

    print(f"{len(antioquia_active)} active stations in Antioquia")
    ```

=== "By category and owner"

    ```python
    ideam_streamflow = client.catalog[
        (client.catalog["category"] == "Limnigráfica") &
        (client.catalog["owner"]    == "IDEAM")
    ]

    print(f"{len(ideam_streamflow)} IDEAM-operated streamflow stations")
    ```

=== "By hydrographic area"

    ```python
    magdalena = client.catalog[
        client.catalog["hydrographic_area"] == "Magdalena - Cauca"
    ]

    print(f"{len(magdalena)} stations in the Magdalena–Cauca watershed")
    ```

!!! info "Unique values for text columns"
    Not sure what the exact spelling for a department or category is?
    Use `.unique()` to see every distinct value in a column:

    ```python
    print(client.catalog["hydrographic_area"].unique())
    print(client.catalog["department"].nunique(), "departments covered")
    ```

---

## Checking which columns are available

The table below lists every column in `client.catalog` and what it contains.

| Column | dtype | Description |
|---|---|---|
| `id` | `str` | Official 8-digit IDEAM station code |
| `name` | `str` | Human-readable station name |
| `category` | `str` | Station type (e.g. `Climática`, `Limnigráfica`) |
| `technology` | `str` | Data-collection method (e.g. `Convencional`) |
| `status` | `str` | `Activa` or `Suspendida` |
| `department` | `str` | Colombian department (uppercase) |
| `municipality` | `str` | Municipality within the department |
| `altitude` | `float` | Elevation above sea level in metres |
| `longitude` | `float` | Decimal-degree longitude (WGS 84) |
| `latitude` | `float` | Decimal-degree latitude (WGS 84) |
| `installation_date` | `datetime64` | Date the station was commissioned |
| `suspension_date` | `datetime64` | Date the station was decommissioned (`NaT` if still active) |
| `hydrographic_area` | `str` | Broad hydrographic area (e.g. `Magdalena - Cauca`) |
| `hydrographic_zone` | `str` | Hydrographic zone within the area |
| `hydrographic_subzone` | `str` | Hydrographic sub-zone within the zone |
| `owner` | `str` | Responsible entity (e.g. `IDEAM`) |
| `geometry` | `Point` | Shapely `Point(longitude, latitude)` |

---

## From catalog rows to full Station objects

Querying `client.catalog` returns lightweight DataFrame rows. They are
useful for discovery and spatial filtering but do not contain variable
metadata or time-series data. To load the complete record for a station,
pass its `id` to `client.fetch_station()`:

```python
# Find the station ID from the catalog
row = client.catalog[client.catalog["name"].str.contains("CALAMAR")]
station_id = row["id"].iloc[0]

# Fetch the full Station object
station = client.fetch_station(station_id)
print(station)
```

!!! warning "One request per station"
    `fetch_station()` makes a live request to the Aquarius WebPortal to
    discover available variables. If you need to hydrate many stations at
    once, use `client.fetch_stations([ids])` or the spatial helpers described
    in [Spatial Queries](spatial.md).

---

## What's next?

With `client.catalog` you have found your stations of interest. Now learn
how to work with the rich metadata and time-series data they expose.

[:octicons-arrow-right-24: Fetching Stations](stations.md)