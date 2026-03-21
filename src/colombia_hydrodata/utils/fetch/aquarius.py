from typing import TypedDict

import pandas as pd
import requests as rq
from aquarius_webportal import AquariusWebPortal

from colombia_hydrodata.utils.cache import save_table
from colombia_hydrodata.utils.endpoints import aquarius_webportal, aquarius_webportal_datasets

WP = AquariusWebPortal(aquarius_webportal)
DATASET_DEFAULT_PARAMS = {
    "sort": "TimeStamp-asc",
    "page": 1,
    "pageSize": int(1e13),
    "interval": "Latest",
    "timezone": -300,
    "alldata": "true",
    "virtual": "true",
}


class DatasetInfo(TypedDict):
    param: str
    label: str
    id: int


@save_table("aquarius_datasets")
def aquarius_datasets() -> pd.DataFrame:
    datasets = []
    for param in WP.fetch_params()["param_name"]:
        datasets.append(WP.fetch_datasets(param_name=param))
    datasets = pd.concat(datasets, ignore_index=True)
    return datasets


def station_datasets(station_id: str) -> dict[str, DatasetInfo]:
    datasets = aquarius_datasets()
    datasets = pd.DataFrame(datasets[datasets["loc_id"] == station_id][["param", "label", "wp_dset_id"]]).rename(columns={"wp_dset_id": "id"})
    datasets = datasets.to_dict(orient="records")
    return {f"{dataset['param']}@{dataset['label']}": dataset for dataset in datasets}  # type: ignore


def dataset(dataset_id: int, params: dict[str, str | float] | None = None) -> pd.DataFrame:
    user_params = {} if not params else params
    response = rq.get(aquarius_webportal_datasets, params=dict(DATASET_DEFAULT_PARAMS, **user_params, **{"dataset": dataset_id}))
    data = pd.DataFrame(response.json()["Data"])
    data["TimeStamp"] = pd.to_datetime(data["TimeStamp"], errors="coerce")
    data["Value"] = pd.to_numeric(data["Value"], errors="coerce")
    return data[["TimeStamp", "Value"]].rename(columns={"TimeStamp": "timestamp", "Value": "value"})  # type: ignore


if __name__ == "__main__":
    df = dataset(dataset_id=514044)
    print(df)
