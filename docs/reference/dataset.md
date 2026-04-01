# Dataset

`Dataset` is a plain dataclass that bundles a `Station` reference, a `Variable` descriptor,
and the fetched time-series data. It is returned by `station.fetch(key)` or `station[key]`.
Access the measurements directly via `dataset.data`, which is a `pandas.DataFrame` with
`timestamp` (datetime) and `value` (float64) columns. Plotting helpers are
available through the `dataset.plot` property.

::: colombia_hydrodata.dataset.Dataset
options:
show_source: false
show_root_heading: true
show_symbol_type_heading: true
show_symbol_type_toc: true
members_order: source
