from typing import Sequence

import geopandas as gpd
import shapely
from shapely.geometry import MultiPolygon, Point, Polygon

from colombia_hydrodata.filters import Filters
from colombia_hydrodata.station import Station
from colombia_hydrodata.utils.fetch.stations import fetch_df


class Client:
    """High-level client for querying and fetching Colombian hydrological station data.

    On instantiation the full station catalog is retrieved from the national
    catalogue (CNE) and stored as a GeoDataFrame.  Every row is assigned a
    Shapely ``Point`` geometry derived from the station's longitude and
    latitude fields, enabling spatial queries directly on the catalog.

    Attributes:
        catalog (gpd.GeoDataFrame): The full station catalog with point
            geometries attached to each row.
    """

    def __init__(self):
        """Initialises the client by fetching the station catalog and attaching point geometries.

        The catalog is retrieved from the CNE endpoint (with caching) and
        stored as a GeoDataFrame whose geometry column contains Shapely
        ``Point`` objects built from each station's longitude and latitude
        fields.
        """
        catalog = fetch_df()
        geo_series = gpd.GeoSeries([Point(x, y) for x, y in zip(catalog["longitude"], catalog["latitude"])])
        self.catalog = gpd.GeoDataFrame(catalog, geometry=geo_series)

    def stations_in_list(self, station_ids: Sequence[str]) -> gpd.GeoDataFrame:
        """Returns a subset of the catalog containing only the specified station IDs.

        Args:
            station_ids: A sequence of station ID strings to look up in the
                catalog.

        Returns:
            A GeoDataFrame containing only the rows whose ``id`` value is
            present in ``station_ids``.
        """
        return gpd.GeoDataFrame(self.catalog[self.catalog["id"].isin(station_ids)])

    def stations_in_region(self, region: Polygon | MultiPolygon) -> gpd.GeoDataFrame:
        """Returns all catalog stations whose geometry falls within a given region.

        Args:
            region: A Shapely ``Polygon`` or ``MultiPolygon`` defining the
                area of interest.

        Returns:
            A GeoDataFrame containing only the stations that lie within
            ``region``.
        """
        return gpd.GeoDataFrame(self.catalog[self.catalog.geometry.within(region)])

    def filter_stations(self, filters: Filters | None = None, subset: gpd.GeoDataFrame | None = None) -> gpd.GeoDataFrame:
        """Applies attribute-based filters to a station GeoDataFrame.

        Each non-``None`` field on the ``Filters`` instance is used as an
        equality constraint against the corresponding column in the
        DataFrame.  All constraints must be satisfied simultaneously (logical
        AND).

        Args:
            filters: A ``Filters`` instance whose non-``None`` fields are
                used as equality constraints.  If ``None`` or otherwise
                falsy, the input DataFrame is returned unchanged.
            subset: The GeoDataFrame to filter.  When ``None``, the full
                ``self.catalog`` is used as the source.

        Returns:
            A GeoDataFrame containing only the rows that satisfy every
            constraint specified in ``filters``.
        """
        df = subset if subset is not None else self.catalog
        if not filters:
            return gpd.GeoDataFrame(df)
        filters_dict = filters.to_dict()
        return gpd.GeoDataFrame(df[df.apply(lambda row: all(getattr(row, k) == v for k, v in filters_dict.items()), axis=1)])

    def fetch_station(self, station_id: str) -> Station:
        """Fetches full metadata and available variables for a single station.

        Args:
            station_id: The unique identifier string of the station to fetch.

        Returns:
            A ``Station`` dataclass populated with the station's metadata,
            location, hydrographic context, and available measurement
            variables.
        """
        return Station.from_stations_df(station_id)

    def fetch_stations(self, station_ids: Sequence[str], filters: Filters | None = None) -> Sequence[Station]:
        """Fetches full ``Station`` objects for a list of station IDs.

        The catalog is first narrowed to the requested IDs and then
        optionally filtered by ``filters`` before each matching station is
        individually fetched.

        Args:
            station_ids: A sequence of station ID strings to fetch.
            filters: An optional ``Filters`` instance used to further
                restrict which stations are returned.

        Returns:
            A sequence of ``Station`` objects for every station that passed
            all filters.
        """
        stations = self.stations_in_list(station_ids)
        stations = self.filter_stations(filters, subset=stations)
        return [self.fetch_station(station_id) for station_id in stations["id"]]

    def fetch_region(self, region: Polygon | MultiPolygon, filters: Filters | None = None) -> Sequence[Station]:
        """Fetches all stations within a geographic region.

        Stations are first narrowed to those that lie within ``region`` and
        then optionally filtered by ``filters`` before being individually
        fetched.

        Args:
            region: A Shapely ``Polygon`` or ``MultiPolygon`` defining the
                area of interest.
            filters: An optional ``Filters`` instance used to further
                restrict which stations within the region are returned.

        Returns:
            A sequence of ``Station`` objects for every station inside
            ``region`` that also passed all filters.
        """
        stations = self.stations_in_region(region)
        stations = self.filter_stations(filters, subset=stations)
        return [self.fetch_station(station_id) for station_id in stations["id"]]

    def fetch_bbox(self, xmin: float, ymin: float, xmax: float, ymax: float, filters: Filters | None = None) -> Sequence[Station]:
        """Fetches all stations within an axis-aligned bounding box.

        The bounding box is constructed from the four corner coordinates and
        converted to a rectangular ``Polygon`` before the spatial query is
        performed.

        Args:
            xmin: Western boundary longitude.
            ymin: Southern boundary latitude.
            xmax: Eastern boundary longitude.
            ymax: Northern boundary latitude.
            filters: An optional ``Filters`` instance used to further
                restrict which stations within the bounding box are returned.

        Returns:
            A sequence of ``Station`` objects for every station inside the
            bounding box that also passed all filters.
        """
        stations = self.stations_in_region(shapely.box(xmin, ymin, xmax, ymax))
        stations = self.filter_stations(filters, subset=stations)
        return [self.fetch_station(station_id) for station_id in stations["id"]]


if __name__ == "__main__":
    client = Client()
    print(client.catalog.info())
