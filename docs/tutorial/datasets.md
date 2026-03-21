# Datasets

A `Dataset` bundles together a station reference, a variable descriptor, and
the complete time series pulled from the IDEAM Aquarius WebPortal. Once you
have a [`Station`](stations.md) object, producing a `Dataset` is a single
expression.

---

## What is a Dataset?

```python
from colombia_hydrodata import Client

client  = Client()
station = client.fetch_station("29037020")
dataset = station["CAUDAL@HIS_Q_MEDIA_D"]
```

`dataset` is a `Dataset` instance — a plain dataclass with three attributes:

| Attribute | Type | Description |
|---|---|---|
| `dataset.station` | `Station` | The station the data comes from |
| `dataset.variable` | `Variable` | Descriptor for the measured variable |
| `dataset.data` | `pd.DataFrame` | Full time-series observations |

Printing a dataset gives a compact one-line summary:

```python
print(dataset)
```

```text
Datset from Station CALAMAR: 29037020, CALAMAR (BOLIVAR), CAUDAL@HIS_Q_MEDIA_D
```

!!! note "Typo in the output"
    `Datset` is the literal text produced by `Dataset.__str__` — the missing
    `a` is in the upstream source. The object itself is fully functional.

---

## Accessing metadata

### `dataset.station`

`dataset.station` is the full `Station` object, so every station attribute is
reachable directly from the dataset:

```python
print(dataset.station.name)        # CALAMAR
print(dataset.station.department)  # BOLIVAR
print(dataset.station.location)    # Location: altitude=8.00 [-74.915; 10.243]
```

### `dataset.variable`

`dataset.variable` is a frozen `Variable` dataclass with three fields:

```python
var = dataset.variable

print(var.param)  # CAUDAL
print(var.label)  # HIS_Q_MEDIA_D
print(var.id)     # numeric Aquarius dataset ID
print(var)        # CAUDAL@HIS_Q_MEDIA_D
```

| Field | Description |
|---|---|
| `var.param` | Parameter family — e.g. `CAUDAL`, `NIVEL`, `PRECIPITACION` |
| `var.label` | Series code that identifies aggregation and sensor — e.g. `HIS_Q_MEDIA_D` |
| `var.id` | Numeric Aquarius dataset identifier used to fetch the raw data |

---

## The `data` DataFrame

`dataset.data` is a `pandas.DataFrame` with exactly two columns:

| Column | dtype | Description |
|---|---|---|
| `timestamp` | `datetime64[ns]` | Date (and time) of the observation |
| `value` | `float64` | Measured value in the variable's native unit |

!!! note "No unit column"
    The unit — m³/s for streamflow, m for gauge level, mm for rainfall, etc.
    — is encoded in the variable key rather than stored in a separate column.
    Use `dataset.variable.param` and `dataset.variable.label` to identify
    what you are working with.

### Viewing the data

```python
print(dataset.data.head())
```

```text
            timestamp     value
0 2000-01-01 05:00:00   1240.80
1 2000-01-02 05:00:00   1179.00
2 2000-01-03 05:00:00   1143.40
3 2000-01-04 05:00:00   1113.60
4 2000-01-05 05:00:00   1066.60
```

```python
print(dataset.data.tail())
```

```text
               timestamp    value
8761 2023-12-27 05:00:00  1834.10
8762 2023-12-28 05:00:00  1801.50
8763 2023-12-29 05:00:00  1768.20
8764 2023-12-30 05:00:00  1740.80
8765 2023-12-31 05:00:00  1693.40
```

### Shape and memory

```python
print(dataset.data.shape)   # (8766, 2)
print(dataset.data.dtypes)
```

```text
timestamp    datetime64[ns]
value               float64
dtype: object
```

### Summary statistics

```python
print(dataset.data["value"].describe())
```

```text
count    8766.000000
mean     1834.512800
std       812.341500
min       312.400000
25%      1148.200000
50%      1681.900000
75%      2412.600000
max      5821.300000
Name: value, dtype: float64
```

---

## Working with the DataFrame

Because `dataset.data` is a standard pandas DataFrame, every familiar
operation works without any conversion.

### Set the timestamp as the index

Most time-series operations become more ergonomic with a `DatetimeIndex`:

```python
df = dataset.data.set_index("timestamp")
```

### Filter by date range

=== "Boolean indexing"

    ```python
    mask = (
        (dataset.data["timestamp"] >= "2020-01-01") &
        (dataset.data["timestamp"] <  "2021-01-01")
    )
    year_2020 = dataset.data[mask]
    print(f"{len(year_2020)} daily records in 2020")
    ```

=== "Using .loc with DatetimeIndex"

    ```python
    df = dataset.data.set_index("timestamp")
    year_2020 = df.loc["2020-01-01":"2020-12-31"]
    print(f"{len(year_2020)} daily records in 2020")
    ```

### Drop missing values

The Aquarius series may contain gaps represented as `NaN`:

```python
clean = dataset.data.dropna(subset=["value"])
print(f"Removed {len(dataset.data) - len(clean)} missing rows")
```

### Resample to monthly means

```python
df      = dataset.data.set_index("timestamp")
monthly = df["value"].resample("ME").mean()

print(monthly.tail(6))
```

```text
timestamp
2023-07-31    2914.8
2023-08-31    3201.4
2023-09-30    3542.1
2023-10-31    3128.7
2023-11-30    2487.3
2023-12-31    1923.6
Freq: ME, Name: value, dtype: float64
```

### Identify annual extremes

```python
df = dataset.data.set_index("timestamp")

print("Highest daily discharge:")
print(df["value"].idxmax(), df["value"].max(), "m³/s")

print("Lowest daily discharge:")
print(df["value"].idxmin(), df["value"].min(), "m³/s")
```

```text
Highest daily discharge:
2011-11-08 05:00:00 5821.3 m³/s

Lowest daily discharge:
2016-03-14 05:00:00 312.4 m³/s
```

---

## Comparing multiple variables

Fetch more than one variable from the same station and align them into a
single DataFrame for side-by-side comparison:

```python
ds_mean = station["NIVEL@NV_MEDIA_D"]
ds_max  = station["NIVEL@NV_MAX_D"]
ds_min  = station["NIVEL@NV_MIN_D"]

gauge = (
    ds_mean.data.set_index("timestamp").rename(columns={"value": "mean"})
    .join(ds_max.data.set_index("timestamp").rename(columns={"value": "max"}))
    .join(ds_min.data.set_index("timestamp").rename(columns={"value": "min"}))
)

print(gauge.head(3))
```

```text
                      mean   max   min
timestamp
2000-01-01 05:00:00   8.42  8.91  8.03
2000-01-02 05:00:00   8.17  8.63  7.82
2000-01-03 05:00:00   7.98  8.44  7.61
```

---

## Exporting the data

=== "CSV"

    ```python
    dataset.data.to_csv("magdalena_q_daily.csv", index=False)
    ```

=== "Excel"

    ```python
    dataset.data.to_excel("magdalena_q_daily.xlsx", index=False)
    ```

=== "Parquet"

    ```python
    dataset.data.to_parquet("magdalena_q_daily.parquet", index=False)
    ```

!!! tip "Include station metadata in the filename"
    A small helper keeps exported files self-describing:

    ```python
    filename = f"{dataset.station.id}_{dataset.variable}.csv".lower()
    # → "29037020_caudal@his_q_media_d.csv"
    dataset.data.to_csv(filename, index=False)
    ```

---

## What's next?

Learn how to discover and fetch stations using bounding boxes and Shapely
polygons.

[:octicons-arrow-right-24: Spatial Queries](spatial.md)