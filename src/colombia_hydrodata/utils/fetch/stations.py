import pandas as pd
import requests

from colombia_hydrodata.utils.cache import save_table
from colombia_hydrodata.utils.endpoints import datos_gov_co_cne
from colombia_hydrodata.utils.transform import transform_stations_df

data_fields = ["id", "name", "category", "technology", "status", "department", "municipality", "installation_date", "suspension_date", "owner"]
location_fields = ["altitude", "longitude", "latitude"]
hydrographic_fields = ["hydrographic_area", "hydrographic_zone", "hydrographic_subzone"]


@save_table("stations")
def fetch_df() -> pd.DataFrame:
    response = requests.get(datos_gov_co_cne, params={"$limit": int(1e13)})
    df = pd.DataFrame.from_records(response.json())
    return transform_stations_df(df)


def station_raw_data(station_id: str) -> dict:
    df = fetch_df()
    return pd.DataFrame(df[df["id"] == station_id]).to_dict(orient="records")[0]


def station_location_data(station_id: str) -> dict:
    data = station_raw_data(station_id)
    return {field: data[field] for field in location_fields}


def station_hydrographic_data(station_id: str) -> dict:
    data = station_raw_data(station_id)
    return {field: data[field] for field in hydrographic_fields}


def station_data(station_id: str) -> dict:
    data = station_raw_data(station_id)
    return {field: data[field] for field in data_fields}
