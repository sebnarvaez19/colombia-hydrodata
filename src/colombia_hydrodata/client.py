from typing import Sequence

import geopandas as gpd
import shapely
from shapely.geometry import MultiPolygon, Point, Polygon

from colombia_hydrodata.filters import Filters
from colombia_hydrodata.station import Station
from colombia_hydrodata.utils.fetch.stations import fetch_df


class Client:
    def __init__(self):
        catalog = fetch_df()
        geo_series = gpd.GeoSeries([Point(x, y) for x, y in zip(catalog["longitude"], catalog["latitude"])])
        self.catalog = gpd.GeoDataFrame(catalog, geometry=geo_series)

    def stations_in_list(self, station_ids: Sequence[str]) -> gpd.GeoDataFrame:
        return gpd.GeoDataFrame(self.catalog[self.catalog["id"].isin(station_ids)])

    def stations_in_region(self, region: Polygon | MultiPolygon) -> gpd.GeoDataFrame:
        return gpd.GeoDataFrame(self.catalog[self.catalog.geometry.within(region)])

    def filter_stations(self, filters: Filters | None = None, subset: gpd.GeoDataFrame | None = None) -> gpd.GeoDataFrame:
        df = subset if subset is not None else self.catalog
        if not filters:
            return gpd.GeoDataFrame(df)
        filters_dict = filters.to_dict()
        return gpd.GeoDataFrame(df[df.apply(lambda row: all(getattr(row, k) == v for k, v in filters_dict.items()), axis=1)])

    def fetch_station(self, station_id: str) -> Station:
        return Station.from_stations_df(station_id)

    def fetch_stations(self, station_ids: Sequence[str], filters: Filters | None = None) -> Sequence[Station]:
        stations = self.stations_in_list(station_ids)
        stations = self.filter_stations(filters, subset=stations)
        return [self.fetch_station(station_id) for station_id in stations["id"]]

    def fetch_region(self, region: Polygon | MultiPolygon, filters: Filters | None = None) -> Sequence[Station]:
        stations = self.stations_in_region(region)
        stations = self.filter_stations(filters, subset=stations)
        return [self.fetch_station(station_id) for station_id in stations["id"]]

    def fetch_bbox(self, xmin: float, ymin: float, xmax: float, ymax: float, filters: Filters | None = None) -> Sequence[Station]:
        stations = self.stations_in_region(shapely.box(xmin, ymin, xmax, ymax))
        stations = self.filter_stations(filters, subset=stations)
        return [self.fetch_station(station_id) for station_id in stations["id"]]


if __name__ == "__main__":
    client = Client()
    stations = client.fetch_bbox(-75.355225, 10.201407, -74.553223, 11.178402, Filters(status="Activa"))
    print(len(stations))
