# Filters

`Filters` is a simple dataclass whose fields correspond to filterable attributes
of the CNE station catalog. Every field defaults to `None`, meaning no constraint
is applied for that dimension. When multiple fields are set, all constraints are
combined with AND logic. Pass a `Filters` instance to `Client.filter_stations()`,
`Client.fetch_stations()`, `Client.fetch_bbox()`, or `Client.fetch_region()`.

::: colombia_hydrodata.filters.Filters
options:
show_source: false
show_root_heading: true
show_symbol_type_heading: true
show_symbol_type_toc: true
members_order: source
