# Data Sources

`colombia-hydrodata` draws from two independent backend systems — a national station
catalog and a time-series portal — because no single API provides both the rich
geospatial metadata _and_ the historical measurements needed for hydrological work.
This page explains each source, what it exposes, and why the two-source design exists.

---

## CNE — National Station Catalog

### What it is

The **Catálogo Nacional de Estaciones (CNE)** is the authoritative registry of all
hydro-meteorological monitoring stations operated or recognised by
[IDEAM](http://www.ideam.gov.co/) (Instituto de Hidrología, Meteorología y Estudios
Ambientales), Colombia's national environmental and meteorological agency. Every
station that has ever been formally registered — active, inactive, or suspended — has
an entry here.

### Where it comes from

The CNE is published as an open dataset on
[datos.gov.co](https://www.datos.gov.co/), Colombia's national open-data portal.
`colombia-hydrodata` retrieves it through the **Socrata Open Data API (SODA)**,
which means:

- No authentication is required for read access.
- The catalog is queried with `$where`, `$limit`, and `$offset` clauses so that
  spatial and attribute filters are pushed down to the server rather than
  transferred as a full table dump.
- The response is GeoJSON-compatible: each station record already carries a
  `geometry` point that can be loaded directly into a `GeoDataFrame`.

!!! note "Catalog freshness"
IDEAM refreshes the CNE periodically; it is **not** a real-time feed. Stations
that were decommissioned recently may still appear, and newly installed stations
may have a short delay before they show up.

### Fields exposed

The CNE record for each station includes the following groups of attributes:

| Field group                   | Example fields                                                   | Purpose                                             |
| ----------------------------- | ---------------------------------------------------------------- | --------------------------------------------------- |
| **Identity**                  | `CODIGO`, `NOMBRE`                                               | Unique station code and human-readable name         |
| **Classification**            | `CATEGORIA`, `TECNOLOGIA`, `ESTADO`                              | Station type, sensor technology, operational status |
| **Ownership**                 | `ENTIDAD`, `SUBRED`                                              | Operating entity and sub-network                    |
| **Location — administrative** | `DEPARTAMENTO`, `MUNICIPIO`, `AREA_OPERATIVA`                    | Political/administrative region                     |
| **Location — hydrographic**   | `AREA_HIDROGRAFICA`, `ZONA_HIDROGRAFICA`, `SUBZONA_HIDROGRAFICA` | Watershed hierarchy                                 |
| **Location — physical**       | `LATITUD`, `LONGITUD`, `ALTITUD`                                 | Geographic coordinates and elevation                |
| **Dates**                     | `FECHA_INSTALACION`, `FECHA_SUSPENSION`                          | Station lifetime                                    |

!!! tip "Using CNE fields as filters"
Most of these field groups map directly to the parameters of the
[`Filters`](../reference/filters.md) object. For instance,
`Filters(department="CUNDINAMARCA", status="Activa")` translates to a SODA
`$where` clause that is evaluated server-side before any data is downloaded.

---

## Aquarius WebPortal — Time-Series Repository

### What it is

**Aquarius** (by Aquatic Informatics / Xylem) is the time-series data management
platform used by IDEAM to store, quality-control, and publish all hydro-meteorological
measurements. The WebPortal is the public-facing REST interface to that database.

Unlike the CNE — which is a flat table of station metadata — Aquarius organises data
in a three-level hierarchy:

```text
Station  ──▶  Dataset (PARAM@LABEL)  ──▶  Time-series points
                 │
                 └─ e.g.  CAUDAL@HIS_Q_MEDIA_D
                          NIVEL@HIS_LG_INST_D
                          TM@HIS_TM_MEDIA_D
```

### Dataset identifiers

Every measurable variable at a station is stored as a named **dataset**. The
identifier exposed by `colombia-hydrodata` is a composite key with the format
`PARAM@LABEL` — see [Variable Keys](variable-keys.md) for the full explanation.

A single station may have dozens of datasets representing different physical parameters,
different time aggregations (instantaneous, daily mean, daily max …), or different
quality tiers.

### What the time series looks like

When you access `.data` on a `Dataset` object, the library queries the Aquarius
WebPortal REST endpoint and returns a `pandas.DataFrame` with:

| Column      | Type             | Description                                             |
| ----------- | ---------------- | ------------------------------------------------------- |
| `timestamp` | `datetime64[ns]` | Observation timestamp                                   |
| `value`     | `float64`        | Measured or derived value in the variable's native unit |

!!! warning "Missing periods"
Aquarius stores time series **sparsely** — only timestamps where a value was
recorded are present. Gaps caused by sensor outages, maintenance windows, or
station suspensions are not filled with `NaN` rows automatically. If your
analysis requires a regular time grid, resample explicitly after fetching:

    ```python
    ts = dataset.data.set_index("timestamp")["value"].resample("1D").mean()
    ```

### Access model

The WebPortal is queried on demand — `colombia-hydrodata` never pre-fetches time
series. Data is only retrieved when you call `station.fetch(key)` or use bracket
notation `station[key]`. This keeps catalog-level operations (filtering, spatial
queries, station inspection) fast even when thousands of stations match your query.

---

## Why two sources?

=== "Separation of concerns"

    The CNE and Aquarius serve fundamentally different purposes:

    - **CNE** answers *"what stations exist, where are they, and what do they
      measure?"*
    - **Aquarius** answers *"what are the actual measurements at this station
      over this time range?"*

    Merging them into a single call would force every spatial query to also
    contact the time-series backend — even when no measurements are needed —
    making simple catalog lookups orders of magnitude slower.

=== "Different update rhythms"

    The CNE is a relatively static registry updated on an administrative schedule,
    while Aquarius receives new measurements continuously (hourly to daily depending
    on the station).  Treating them as separate layers means the library can cache
    catalog results aggressively without risking stale measurement data.

=== "Different authentication models"

    The CNE SODA API is fully public.  Aquarius may require institutional credentials
    for certain datasets.  Keeping the layers separate means unauthenticated users
    can still perform spatial queries and inspect station metadata even if they cannot
    download restricted time series.

!!! info "How the library bridges the gap"
A `Station` object returned by the `Client` holds the CNE metadata _and_
the Aquarius variable catalogue — all fetched eagerly at construction time.
Accessing `station.variables` is always fast (no network call). Only requesting
the actual time-series data via `station[key]` triggers an Aquarius request.

---

## Summary

|                         | CNE Catalog                     | Aquarius WebPortal                    |
| ----------------------- | ------------------------------- | ------------------------------------- |
| **Provider**            | IDEAM via datos.gov.co          | IDEAM Aquarius installation           |
| **Protocol**            | SODA REST (GeoJSON)             | Aquarius WebPortal REST               |
| **Auth required**       | No                              | Sometimes                             |
| **Content**             | Station registry & metadata     | Hydrological time series              |
| **Update frequency**    | Periodic (administrative)       | Continuous (near real-time)           |
| **Library entry point** | `Client.fetch_*()` methods      | `station[key]` / `station.fetch(key)` |
| **Output type**         | `GeoDataFrame` / `Station` list | `pandas.DataFrame`                    |
