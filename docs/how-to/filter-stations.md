# Filtering Stations

The `Filters` object lets you narrow down which hydrological stations are returned by any
spatial or list-based query. Every field is optional — omitting a field (or passing `None`)
means **no constraint is applied** for that dimension. When you supply more than one field,
all constraints are combined with **AND** logic.

---

## The `Filters` Dataclass

```python
from colombia_hydrodata import Filters

Filters(
    category=None,
    department=None,
    municipality=None,
    status=None,
    owner=None,
    hydrographic_area=None,
    hydrographic_zone=None,
    hydrographic_subzone=None,
)
```

| Parameter | Type | Example value |
|---|---|---|
| `category` | `str` | `"Limnigráfica"` |
| `department` | `str` | `"Antioquia"` |
| `municipality` | `str` | `"Medellín"` |
| `status` | `str` | `"Activa"` |
| `owner` | `str` | `"IDEAM"` |
| `hydrographic_area` | `str` | `"Magdalena - Cauca"` |
| `hydrographic_zone` | `str` | `"Alto Magdalena"` |
| `hydrographic_subzone` | `str` | `"Río Bogotá"` |

!!! note "None means no filter"
    Every parameter defaults to `None`. A `None` value is simply **ignored** during
    filtering — it does not exclude stations that lack that attribute.

---

## Filtering by Individual Fields

Use `client.filter_stations(filters)` to narrow down `client.catalog` by any combination
of attributes. It returns a `GeoDataFrame` — no network requests are made beyond the
initial catalog load. To get full `Station` objects (with time-series access) call
`client.fetch_station(id)` on the IDs you care about.

=== "Category"

    Station categories reflect the type of measurement equipment installed at the site.
    Common values include `"Limnigráfica"`, `"Limnimétrica"`, `"Climática Ordinaria"`,
    and `"Pluviométrica"`.

    ```python
    from colombia_hydrodata import Client, Filters

    client = Client()

    # Returns a GeoDataFrame of matching catalog rows
    filters = Filters(category="Limnigráfica")
    gdf = client.filter_stations(filters)
    print(f"{len(gdf)} stations found")
    ```

=== "Department"

    Use the full Spanish-language department name as it appears in the CNE catalog.

    ```python
    from colombia_hydrodata import Client, Filters

    client = Client()

    filters = Filters(department="Cundinamarca")
    gdf = client.filter_stations(filters)
    print(f"{len(gdf)} stations in Cundinamarca")
    ```

=== "Municipality"

    Municipalities must match the CNE catalog spelling exactly.

    ```python
    from colombia_hydrodata import Client, Filters

    client = Client()

    filters = Filters(municipality="Villavicencio")
    gdf = client.filter_stations(filters)
    ```

=== "Status"

    Typical status values are `"Activa"` (operational) and `"Suspendida"` (suspended).
    Filter to active stations to avoid requesting time series for decommissioned sites.

    ```python
    from colombia_hydrodata import Client, Filters

    client = Client()

    filters = Filters(status="Activa")
    gdf = client.filter_stations(filters)
    ```

=== "Owner"

    The `owner` field identifies the institution responsible for the station.
    IDEAM is the primary national network operator, but regional agencies
    (e.g. CAR, CORNARE, CORPOAMAZONIA) also maintain stations in the catalog.

    ```python
    from colombia_hydrodata import Client, Filters

    client = Client()

    filters = Filters(owner="IDEAM")
    gdf = client.filter_stations(filters)
    ```

=== "Hydrographic Area / Zone / Subzone"

    The CNE catalog follows Colombia's official hydrographic zonification.
    You can filter at three levels of granularity:

    ```python
    from colombia_hydrodata import Client, Filters

    client = Client()

    # Broadest level — hydrographic area
    filters = Filters(hydrographic_area="Magdalena - Cauca")
    gdf = client.filter_stations(filters)

    # Intermediate level — hydrographic zone
    filters = Filters(hydrographic_zone="Alto Magdalena")
    gdf = client.filter_stations(filters)

    # Finest level — hydrographic subzone
    filters = Filters(hydrographic_subzone="Río Bogotá")
    gdf = client.filter_stations(filters)
    ```

---

## Using Filters with Each Query Method

`Filters` can be passed to **any** of the three client query methods.

=== "fetch_stations"

    Fetch a specific list of station IDs and apply filters as a post-query mask.
    `station_ids` is a required argument — supply the IDs you already know.

    ```python
    from colombia_hydrodata import Client, Filters

    client = Client()

    ids = ["21207010", "21207020", "21207030", "23197010"]
    filters = Filters(status="Activa", owner="IDEAM")

    stations = client.fetch_stations(ids, filters=filters)
    ```

=== "fetch_bbox"

    Returns all stations whose coordinates fall inside the bounding box **and** match
    the filters.

    ```python
    from colombia_hydrodata import Client, Filters

    client = Client()

    # Bounding box around the Bogotá Savanna (WGS 84)
    xmin, ymin, xmax, ymax = -74.4, 4.4, -73.9, 4.9

    filters = Filters(category="Limnigráfica", status="Activa")
    stations = client.fetch_bbox(xmin, ymin, xmax, ymax, filters=filters)
    ```

=== "fetch_region"

    Accepts a Shapely `Polygon` or `MultiPolygon` and applies an additional attribute
    filter on top of the spatial intersection.

    ```python
    from shapely.geometry import Polygon
    from colombia_hydrodata import Client, Filters

    client = Client()

    watershed = Polygon([
        (-75.8, 6.0), (-74.5, 6.0),
        (-74.5, 7.2), (-75.8, 7.2),
        (-75.8, 6.0),
    ])

    filters = Filters(hydrographic_area="Magdalena - Cauca", status="Activa")
    stations = client.fetch_region(watershed, filters=filters)
    ```

---

## Combining Multiple Filters

All supplied fields are joined with **AND**. A station must satisfy *every*
non-`None` condition to be included in the result.

```python
from colombia_hydrodata import Client, Filters

client = Client()

# Active, IDEAM-owned, limnigraphic stations in Antioquia
# on the Cauca hydrographic subzone
filters = Filters(
    category="Limnigráfica",
    department="Antioquia",
    status="Activa",
    owner="IDEAM",
    hydrographic_subzone="Río Cauca entre ríos Cañas y Nechí",
)

# filter_stations returns a GeoDataFrame of matching catalog rows
gdf = client.filter_stations(filters)
print(f"Found {len(gdf)} stations matching all criteria")

# Fetch full Station objects for those rows if needed
station_objects = [client.fetch_station(sid) for sid in gdf["id"]]
```

!!! warning "AND logic only"
    There is no built-in OR operator across `Filters` fields. If you need stations
    from *either* Antioquia *or* Caldas, run two separate filter calls and concatenate:

    ```python
    import pandas as pd
    import geopandas as gpd

    f_ant = Filters(department="Antioquia", status="Activa")
    f_cal = Filters(department="Caldas",    status="Activa")

    gdf_ant = client.filter_stations(f_ant)
    gdf_cal = client.filter_stations(f_cal)

    # Merge and drop duplicate station IDs
    combined = gpd.GeoDataFrame(pd.concat([gdf_ant, gdf_cal]).drop_duplicates(subset="id"))
    ```

---

## Quick-Reference Cheatsheet

```python
from colombia_hydrodata import Client, Filters

client = Client()

# 1. Single-field filter (returns GeoDataFrame)
Filters(department="Boyacá")

# 2. Active stations only
Filters(status="Activa")

# 3. Specific owner + category
Filters(owner="IDEAM", category="Pluviométrica")

# 4. Full hydrographic path
Filters(
    hydrographic_area="Orinoco",
    hydrographic_zone="Meta",
    hydrographic_subzone="Río Metica (Guamal - Humadea)",
)

# 5. Catalog-level filter — returns GeoDataFrame
gdf = client.filter_stations(Filters(status="Activa", department="Antioquia"))

# 6. Spatial query with attributes — returns list[Station]
stations = client.fetch_bbox(-77.0, 1.0, -76.0, 2.0)
```

!!! info "Case sensitivity"
    Filter values are matched against the CNE catalog strings, which use title-case
    Spanish. Make sure your strings match the catalog spelling exactly
    (including accented characters such as `á`, `é`, `ó`).