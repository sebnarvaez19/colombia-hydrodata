# Spatial Queries

`colombia-hydrodata` supports three levels of spatial querying: a fast
axis-aligned bounding box, an arbitrary Shapely polygon, and lightweight
catalog-only lookups that avoid any additional network requests.

!!! note "Coordinate reference system"
    All coordinates used throughout the library are in **WGS 84 (EPSG:4326)**,
    with **longitude as the X axis** and **latitude as the Y axis**.
    No automatic CRS conversion is performed — make sure any polygons you
    build or load from external files use the same reference system before
    passing them to the client.

---

## Bounding box — `fetch_bbox`

The quickest way to pull all stations inside a rectangular area is
`fetch_bbox`. Pass the four edges of the rectangle and get back a list of
fully-hydrated [`Station`](stations.md) objects.

```python
from colombia_hydrodata import Client

client = Client()

# Approximate bounding box covering the department of Antioquia
stations = client.fetch_bbox(
    xmin=-77.15,  # western longitude
    ymin=  5.40,  # southern latitude
    xmax=-73.85,  # eastern longitude
    ymax=  8.90,  # northern latitude
)

print(f"Found {len(stations)} stations")
for s in stations[:4]:
    print(f"  {s.id}  {s.name}  ({s.category})")
```

```text
Found 312 stations
  29040010  RÍO NARE EN LA VUELTA            (Limnigráfica)
  29045020  RÍO SAMANÁ NORTE EN PUERTO GARZA (Limnigráfica)
  29053010  RÍO PORCE EN PUERTO VALDIVIA     (Limnigráfica)
  29060010  RÍO NECHÍ EN CAUCASIA            (Limnigráfica)
```

### Combining with `Filters`

Pass a [`Filters`](../reference/filters.md) object to narrow the results
without changing the spatial boundary:

```python
from colombia_hydrodata import Client, Filters

client = Client()

stations = client.fetch_bbox(
    xmin=-77.15, ymin=5.40,
    xmax=-73.85, ymax=8.90,
    filters=Filters(category="Limnigráfica", status="Activa"),
)

print(f"Found {len(stations)} active streamflow stations in the bounding box")
```

!!! warning "Large bounding boxes trigger many requests"
    Every station in the result requires an individual round-trip to the
    Aquarius WebPortal to discover available variables.  For very large areas,
    use [`stations_in_region`](#catalog-only-queries-stations_in_region) first
    to preview the station count before committing to a full fetch.

---

## Polygon region — `fetch_region`

For non-rectangular study areas, pass any Shapely `Polygon` or
`MultiPolygon` to `fetch_region`:

```python
from shapely.geometry import Polygon
from colombia_hydrodata import Client

client = Client()

# Approximate boundary around the Bogotá River sub-basin
bogota_basin = Polygon([
    (-74.50, 3.70),
    (-73.60, 3.70),
    (-73.60, 5.30),
    (-74.50, 5.30),
    (-74.50, 3.70),
])

stations = client.fetch_region(bogota_basin)
print(f"Found {len(stations)} stations inside the polygon")
```

### Loading polygon boundaries from files

Real study areas seldom fit a simple rectangle.  You can load boundaries
from any geospatial file format and pass the geometry directly:

=== "GeoJSON"

    ```python
    import geopandas as gpd
    from colombia_hydrodata import Client

    client  = Client()
    gdf     = gpd.read_file("study_area.geojson").to_crs(epsg=4326)
    region  = gdf.geometry.union_all()   # merge features into one polygon

    stations = client.fetch_region(region)
    print(f"Found {len(stations)} stations")
    ```

=== "Shapefile"

    ```python
    import geopandas as gpd
    from colombia_hydrodata import Client

    client  = Client()
    gdf     = gpd.read_file("watershed_boundary.shp").to_crs(epsg=4326)
    region  = gdf.geometry.union_all()

    stations = client.fetch_region(region)
    print(f"Found {len(stations)} stations")
    ```

!!! tip "Always reproject to EPSG:4326 first"
    Colombian datasets are often distributed in MAGNA-SIRGAS / Colombia Bogotá
    Zone (EPSG:3116) or other local projections.  Calling `.to_crs(epsg=4326)`
    before extracting the geometry ensures the spatial query works correctly.

---

## Catalog-only queries — `stations_in_region`

When you only need to explore which stations exist in an area — without
loading variable metadata — use `stations_in_region`.  It filters
`client.catalog` in memory and returns a `GeoDataFrame` slice with **zero
additional network requests**.

```python
from shapely.geometry import Polygon
from colombia_hydrodata import Client

client = Client()

bogota_basin = Polygon([
    (-74.50, 3.70),
    (-73.60, 3.70),
    (-73.60, 5.30),
    (-74.50, 5.30),
    (-74.50, 3.70),
])

catalog_slice = client.stations_in_region(bogota_basin)
print(catalog_slice[["id", "name", "category", "status"]].to_string())
```

```text
           id                         name          category      status
0    21018010                       SUESCA      Limnigráfica      Activa
1    21019020                  VILLAPINZÓN     Pluviométrica      Activa
2    21020010                    CHOCONTÁ      Limnigráfica      Activa
3    21021010                    ZIPAQUIRÁ       Climática        Activa
4    21022010                    ZIPAQUIRÁ     Pluviométrica   Suspendida
...
```

### Selectively hydrating stations

Inspect the catalog slice first, then fetch only the stations you actually
need:

```python
# Keep only active limnigraphic stations
active = catalog_slice[
    (catalog_slice["status"]   == "Activa") &
    (catalog_slice["category"] == "Limnigráfica")
]

station_ids = active["id"].tolist()
print(f"Fetching {len(station_ids)} stations …")

stations = client.fetch_stations(station_ids)
```

This two-step approach — preview with `stations_in_region`, then fetch with
`fetch_stations` — is the recommended pattern when working with large or
unfamiliar study areas.

---

## Catalog-only list lookup — `stations_in_list`

If you already know the station IDs you want, `stations_in_list` returns
their catalog rows without making any network requests:

```python
subset = client.stations_in_list(["29037020", "29040010", "21018010"])
print(subset[["id", "name", "department"]])
```

```text
           id                    name    department
0    21018010                  SUESCA  CUNDINAMARCA
1    29037020                 CALAMAR       BOLIVAR
2    29040010   RÍO NARE EN LA VUELTA     ANTIOQUIA
```

!!! info "Row order follows the catalog, not your input list"
    The returned GeoDataFrame preserves the original catalog index order,
    not the order of the IDs you passed in.  Sort or reindex afterwards if
    insertion order matters.

---

## Method comparison

| Method | Input | Returns | Network requests |
|---|---|---|---|
| `fetch_bbox(xmin, ymin, xmax, ymax)` | Four floats | `list[Station]` | One per matched station |
| `fetch_region(polygon)` | Shapely geometry | `list[Station]` | One per matched station |
| `stations_in_region(polygon)` | Shapely geometry | `GeoDataFrame` | **None** |
| `stations_in_list([ids])` | List of ID strings | `GeoDataFrame` | **None** |

Use the catalog-only methods (`stations_in_region`, `stations_in_list`)
when exploring or counting stations.  Switch to the fetch methods
(`fetch_region`, `fetch_bbox`) only when you need full variable metadata and
time-series access.