# Attributes

## Location

`Location` is a frozen dataclass that holds the physical position of a station.
It contains three numeric fields: `altitude` (metres above sea level), `longitude`
(decimal degrees), and `latitude` (decimal degrees).

::: colombia_hydrodata.attributes.Location
    options:
      show_source: false
      show_root_heading: true
      show_symbol_type_heading: true
      show_symbol_type_toc: true
      members_order: source

---

## Hydrographic

`Hydrographic` describes the hydrological context of a station within Colombia's river basin hierarchy, including the area, zone, sub-zone, and catchment to which it belongs. These attributes are useful for grouping or filtering stations by watershed.

::: colombia_hydrodata.attributes.Hydrographic
    options:
      show_source: false
      show_root_heading: true
      show_symbol_type_heading: true
      show_symbol_type_toc: true
      members_order: source

---

## Variable

`Variable` is a frozen dataclass representing a single hydrometeorological time series
available at a station. It carries three fields: `param` (the physical parameter family,
e.g. `"CAUDAL"`), `label` (the Aquarius dataset label, e.g. `"HIS_Q_MEDIA_D"`), and
`id` (the numeric Aquarius dataset identifier used to fetch the raw data).

::: colombia_hydrodata.attributes.Variable
    options:
      show_source: false
      show_root_heading: true
      show_symbol_type_heading: true
      show_symbol_type_toc: true
      members_order: source