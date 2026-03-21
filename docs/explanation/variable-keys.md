# Variable Keys

Every time-series dataset attached to a station is identified by a **variable key** — a short string
that tells you both *what* is being measured and *which specific dataset* inside Aquarius holds the
data. Understanding this format is essential before you start requesting or analysing time series.

---

## The `PARAM@LABEL` Format

A variable key is always written as two parts separated by an at-sign (`@`):

```text
PARAM@LABEL
```

| Part | Meaning | Example |
|------|---------|---------|
| `PARAM` | Physical parameter — the hydrometeorological quantity being measured | `CAUDAL` |
| `LABEL` | Aquarius dataset label — the specific processing level or aggregation stored in the WebPortal | `HIS_Q_MEDIA_D` |

Together they form an unambiguous pointer to a single dataset:

```text
CAUDAL@HIS_Q_MEDIA_D
```

This reads as: *"the daily mean discharge dataset labelled `HIS_Q_MEDIA_D` inside Aquarius"*.

!!! note "Why two parts?"
    A single station can have **multiple datasets for the same physical parameter** — for instance,
    both a raw instantaneous record and a quality-controlled daily mean for water level. The `PARAM`
    component lets you filter by what you care about, while `LABEL` lets you pick the exact
    processing variant you need.

---

## What `PARAM` Represents

`PARAM` is the physical quantity being measured. It is derived from the CNE catalog and standardised
across all stations. Common values are listed in the table below.

| `PARAM` | Physical quantity | Typical unit |
|---------|------------------|--------------|
| `CAUDAL` | Streamflow / discharge | m³/s |
| `NIVEL` | Water-surface gauge height | m |
| `PRECIPITACION` | Rainfall / precipitation | mm |
| `TM` | Suspended-sediment transport | ton/day |
| `TEMPERATURA AIRE` | Air temperature | °C |
| `TEMPERATURA AGUA` | Water temperature | °C |
| `HUMEDAD` | Relative humidity | % |
| `EVAPORACION` | Evaporation | mm |
| `BRILLO SOLAR` | Sunshine duration | hours |
| `VIENTO VELOCIDAD` | Wind speed | m/s |
| `VIENTO DIRECCION` | Wind direction | degrees |
| `PRESION` | Atmospheric pressure | hPa |

!!! tip "Case sensitivity"
    `PARAM` values are **upper-case** as returned by the API. Always use the exact casing shown
    when constructing a key manually or filtering a dictionary.

---

## What `LABEL` Represents

`LABEL` is the dataset label assigned inside the **Aquarius WebPortal** by IDEAM. It encodes
information about the measurement frequency, processing level, and variable abbreviation using a
conventional naming scheme.

A typical label such as `HIS_Q_MEDIA_D` can be read left-to-right:

```text
HIS   _  Q    _  MEDIA  _  D
 │       │       │         └─ Temporal resolution  (D = daily, H = hourly, M = monthly …)
 │       │       └─────────── Statistic             (MEDIA = mean, MAX = maximum, MIN = minimum …)
 │       └─────────────────── Variable abbreviation (Q = discharge, H = gauge height …)
 └─────────────────────────── Dataset family        (HIS = historical series)
```

!!! info "Labels are not guaranteed to be uniform"
    IDEAM does not enforce a strict naming convention across all stations or all variables. Treat
    `LABEL` as an opaque identifier — always **discover** it programmatically rather than
    hard-coding it.

---

## Discovering Available Keys

### Print the Station object

The quickest way to see every key available for a station is to print it:

```python
from colombia_hydrodata import Client

client = Client()
st = client.fetch_station("35127070")

print(list(st.variables.keys()))
```

This shows every key available for the station:

```text
['CAUDAL@HIS_Q_MEDIA_D', 'CAUDAL@HIS_Q_MX_M', 'CAUDAL@HIS_Q_MEDIA_M', 'CAUDAL@Q_MN_D',
 'CAUDAL@Q_MN_M', 'CAUDAL@Q_MX_D', 'CAUDAL@Q_MX_M', 'CAUDAL@Q_MN_A', 'CAUDAL@Q_MX_A',
 'CAUDAL@Q_MEDIA_A', 'CAUDAL@CAUDAL_H', 'NIVEL@NVLM_CON', 'NIVEL@HIS_NV_MEDIA_D',
 'NIVEL@HIS_NV_MN_M', 'NIVEL@HIS_NV_MX_M', 'NIVEL@NIVEL_H', 'NIVEL@NV_MEDIA_D',
 'NIVEL@NV_MN_D', 'NIVEL@NV_MN_M', 'NIVEL@NV_MX_D', 'NIVEL@NV_MX_M', 'NIVEL@NV_MN_A',
 'NIVEL@NV_MX_A', 'NIVEL@NV_MEDIA_A', 'NIVEL@HIS_NIVEL_H', 'TM@HIS_TR_QS_M',
 'TM@HIS_TR_QS_TT_M', 'TM@HIS_TR_QS_MX_M', 'TM@HIS_TR_KT/D_QS_D']
```

### Inspect the `variables` dictionary

Every `Station` exposes a `variables` attribute — a dictionary keyed by the variable key and
valued with dataset metadata:

=== "List all keys"

    ```python
    for key in st.variables:
        print(key)
    # CAUDAL@HIS_Q_MEDIA_D
    # NIVEL@HIS_H_MEDIA_D
    # …
    ```

=== "Filter by PARAM"

    ```python
    discharge_keys = [k for k in st.variables if k.startswith("CAUDAL@")]
    print(discharge_keys)
    # ['CAUDAL@HIS_Q_MEDIA_D', 'CAUDAL@HIS_Q_INST_15']
    ```

=== "Inspect a single Variable"

    ```python
    var = st.variables["CAUDAL@HIS_Q_MEDIA_D"]
    print(var.param)   # CAUDAL
    print(var.label)   # HIS_Q_MEDIA_D
    print(var.id)      # Numeric Aquarius dataset identifier
    print(var)         # CAUDAL@HIS_Q_MEDIA_D
    ```

### Use the `in` operator

Before requesting a dataset it is good practice to confirm it exists:

```python
key = "NIVEL@NV_MEDIA_D"

if key in st:
    ds = st[key]
    print(ds.data.head())
else:
    print(f"Key {key!r} is not available for station {st.id}")
```

!!! warning "Availability varies by station"
    Not every station records every parameter. A key that exists for one station may be absent from
    another even within the same river basin. Always check before fetching.

---

## Requesting a Dataset by Key

Once you have identified the key, use bracket notation or `station.fetch()` — they are equivalent:

=== "Single dataset"

    ```python
    ds = st["CAUDAL@HIS_Q_MEDIA_D"]
    # or: ds = st.fetch("CAUDAL@HIS_Q_MEDIA_D")

    print(ds.data.head())
    #              timestamp    value
    # 0  2000-01-01 05:00:00  1240.80
    ```

=== "Multiple datasets"

    ```python
    import pandas as pd

    keys = ["NIVEL@NV_MEDIA_D", "NIVEL@NV_MAX_D", "NIVEL@NV_MIN_D"]
    frames = {k: st[k].data.set_index("timestamp")["value"] for k in keys if k in st}

    combined = pd.DataFrame(frames)
    print(combined.head())
    ```

=== "All discharge datasets"

    ```python
    import pandas as pd

    discharge_keys = [k for k in st.variables if k.startswith("CAUDAL@")]
    frames = {}

    for key in discharge_keys:
        frames[key] = st[key].data.set_index("timestamp")["value"]

    combined = pd.DataFrame(frames)
    ```

---

## Key Anatomy — Quick Reference

```text
┌──────────────────────────────────────────────────────┐
│  CAUDAL @ HIS_Q_MEDIA_D                              │
│  ──────   ─────────────                              │
│  PARAM    LABEL                                      │
│                                                      │
│  Physical  Aquarius dataset identifier               │
│  quantity  (family _ var _ statistic _ resolution)   │
└──────────────────────────────────────────────────────┘
```

!!! summary "Key takeaways"
    - Variable keys have the form `PARAM@LABEL`.
    - `PARAM` identifies the physical quantity (e.g. `CAUDAL`, `NIVEL`, `PRECIPITACION`).
    - `LABEL` is the opaque Aquarius dataset identifier — discover it, don't guess it.
    - Use `st.variables` to enumerate available keys, and the `in` operator to guard against
      missing datasets before fetching.