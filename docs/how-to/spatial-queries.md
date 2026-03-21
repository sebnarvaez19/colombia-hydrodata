# Spatial Queries

This guide shows you how to retrieve hydrological stations by location — whether that's a bounding box, a custom polygon, a GeoJSON file, or a plain list of station IDs.

---

## Overview

`Client` exposes three spatial entry-points:

| Method | Input | Returns |
|---|---|---|
| `fetch_bbox(xmin, ymin, xmax, ymax, filters)` | Bounding box coordinates | `list[Station]` |
| `fetch_region(polygon, filters)` | Shapely `Polygon` / `MultiPolygon` | `list[Station]` |
| `fetch_stations(ids, filters)` | List of station ID strings | `list[Station]` |
| `stations_in_region(polygon)` | Shapely `Polygon` / `MultiPolygon` | `GeoDataFrame` |
| `stations_in_list(ids)` | List of station ID strings | `GeoDataFrame` |

The first three return fully hydrated `Station` objects (catalog metadata **+** time-series access). The last two return a lightweight `GeoDataFrame` of catalog metadata only — useful for quick exploration without fetching dataset descriptors.

---

## Quick Recipes

### Bounding box

Pass WGS-84 coordinates in the order `(xmin, ymin, xmax, ymax)` — i.e. `(west, south, east, north)`.

```python
from colombia_hydrodata import Client

client = Client()

# Rough bounding box around Bogotá D.C.
stations = client.fetch_bbox(
    xmin=-74.22,
    ymin=4.45,
    xmax=-73.99,
    ymax=4.84,
)

for st in stations:
    print(st.id, st.name)
```

---

### Polygon from coordinates

Build a Shapely polygon directly when you have a known geometry.

```python
from shapely.geometry import Polygon
from colombia_hydrodata import Client

client = Client()

# Rough outline of the Cauca Valley
cauca_valley = Polygon([
    (-76.70, 3.60),
    (-75.50, 3.60),
    (-75.50, 5.00),
    (-76.70, 5.00),
    (-76.70, 3.60),
])

stations = client.fetch_region(cauca_valley)
```

---

### Polygon from a GeoJSON file

=== "geopandas"

    ```python
    import geopandas as gpd
    from colombia_hydrodata import Client

    client = Client()

    boundary = gpd.read_file("magdalena_basin.geojson")
    # Dissolve all features into a single polygon
    polygon = boundary.dissolve().geometry.iloc[0]

    stations = client.fetch_region(polygon)
    ```

=== "shapely + json"

    ```python
    import json
    from shapely.geometry import shape
    from colombia_hydrodata import Client

    client = Client()

    with open("magdalena_basin.geojson") as f:
        geojson = json.load(f)

    # Assumes a single Feature or the first Feature in a FeatureCollection
    feature = (
        geojson["features"][0]
        if geojson["type"] == "FeatureCollection"
        else geojson
    )
    polygon = shape(feature["geometry"])

    stations = client.fetch_region(polygon)
    ```

---

### List of known station IDs

```python
from colombia_hydrodata import Client

client = Client()

station_ids = ["21207020", "21207050", "24017010"]
stations = client.fetch_stations(station_ids)
```

---

## Catalog Only vs. Full Station Objects

Use the lightweight helpers when you only need metadata — they skip the Aquarius WebPortal handshake and return immediately as a `GeoDataFrame`.

=== "Catalog only (fast)"

    ```python
    from shapely.geometry import Polygon
    from colombia_hydrodata import Client

    client = Client()

    polygon = Polygon([(-74.5, 4.0), (-73.5, 4.0), (-73.5, 5.0), (-74.5, 5.0), (-74.5, 4.0)])

    # Returns a GeoDataFrame — no Station objects, no dataset descriptors
    gdf = client.stations_in_region(polygon)
    print(gdf.columns.tolist())
    print(gdf.head())
    ```

=== "Full Station objects (rich)"

    ```python
    from shapely.geometry import Polygon
    from colombia_hydrodata import Client

    client = Client()

    polygon = Polygon([(-74.5, 4.0), (-73.5, 4.0), (-73.5, 5.0), (-74.5, 5.0), (-74.5, 4.0)])

    # Returns list[Station] — each object holds dataset descriptors
    # and provides access to time-series data
    stations = client.fetch_region(polygon)

    for st in stations:
        print(st.id, list(st.variables.keys()))
    ```

!!! tip "When to use which"
    - Exploring station coverage? → `stations_in_region` / `stations_in_list`
    - Downloading time-series data? → `fetch_region` / `fetch_bbox` / `fetch_stations`

---

## Combining Spatial Queries with Filters

Every `fetch_*` method accepts an optional `Filters` object. Spatial extent and attribute filters are evaluated together with **AND** logic — only stations that satisfy **both** the geometry test and every non-`None` filter field are returned.

```python
from shapely.geometry import Polygon
from colombia_hydrodata import Client, Filters

client = Client()

# Only active IDEAM stream-gauge stations within the bounding polygon
filters = Filters(
    category="Limnigráfica",
    status="Activa",
    owner="IDEAM",
)

andes_region = Polygon([
    (-77.0, 1.0),
    (-72.0, 1.0),
    (-72.0, 8.0),
    (-77.0, 8.0),
    (-77.0, 1.0),
])

stations = client.fetch_region(andes_region, filters=filters)
print(f"{len(stations)} stations matched")
```

See the [Filter Stations](filter-stations.md) guide for a full reference on every `Filters` field.

---

## Inspecting Results as a GeoDataFrame

All `fetch_*` results can easily be converted to a `GeoDataFrame` for spatial analysis:

```python
import geopandas as gpd
from shapely.geometry import Point
from colombia_hydrodata import Client

client = Client()

stations = client.fetch_bbox(-75.5, 5.5, -75.0, 6.0)

gdf = gpd.GeoDataFrame(
    [{"id": st.id, "name": st.name, "geometry": Point(st.longitude, st.latitude)}
     for st in stations],
    crs="EPSG:4326",
)

gdf.to_file("results.gpkg", driver="GPKG")
```

---

## ⚠ Warning: Large Regions

!!! warning "Large spatial queries can be slow"
    Querying large regions (e.g. the entire Orinoco or Amazon basin) may match hundreds
    of stations. Because `fetch_region` and `fetch_bbox` hydrate each `Station` object —
    which includes a round-trip to the Aquarius WebPortal per station — large result sets
    can take **several minutes**.

    **Strategies to manage this:**

    - Use `stations_in_region` first to count matches before committing to a full fetch.
    - Add `Filters` to narrow the result set (e.g. `status="Activa"`, `category="Limnigráfica"`).
    - Break a large region into smaller tiles and process them incrementally.

```python
from colombia_hydrodata import Client, Filters
from shapely.geometry import Polygon

client = Client()

large_polygon = Polygon([(-79.0, -4.0), (-66.0, -4.0), (-66.0, 12.0), (-79.0, 12.0), (-79.0, -4.0)])

# Step 1: cheap catalog scan
gdf = client.stations_in_region(large_polygon)
print(f"Found {len(gdf)} stations in region")

# Step 2: decide whether to proceed or refine
if len(gdf) > 100:
    print("Too many stations — applying additional filters")
    filters = Filters(status="Activa", category="Limnigráfica")
    stations = client.fetch_region(large_polygon, filters=filters)
else:
    stations = client.fetch_region(large_polygon)
```

---

## Related Pages

- [Filter Stations](filter-stations.md) — full reference for the `Filters` class
- [Architecture](../explanation/architecture.md) — how `Client`, `Station`, and `Dataset` relate
- [Variable Keys](../explanation/variable-keys.md) — how to work with `PARAM@LABEL` keys once you have `Station` objects