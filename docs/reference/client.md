# Client

The `Client` class is the main entry point for querying Colombian hydrological station data.
On instantiation it downloads the full CNE station catalog from datos.gov.co and stores it
as a `GeoDataFrame` in `client.catalog`. No API key or authentication is required — both
data sources used by the library are publicly accessible.

::: colombia_hydrodata.client.Client
options:
show_source: false
show_root_heading: true
show_symbol_type_heading: true
show_symbol_type_toc: true
members_order: source
