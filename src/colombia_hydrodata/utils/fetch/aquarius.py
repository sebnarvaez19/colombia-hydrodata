from typing import TypedDict

import pandas as pd
from aquarius_webportal import AquariusWebPortal

from colombia_hydrodata.utils.cache import save_table
from colombia_hydrodata.utils.endpoints import aquarius_webportal

wp = AquariusWebPortal(aquarius_webportal)


class DatasetInfo(TypedDict):
    param: str
    label: str
    id: int


@save_table("aquarius_datasets")
def aquarius_datasets() -> pd.DataFrame:
    datasets = []
    for param in wp.fetch_params()["param_name"]:
        datasets.append(wp.fetch_datasets(param_name=param))
    datasets = pd.concat(datasets, ignore_index=True)
    return datasets


def station_datasets(station_id: str) -> dict[str, DatasetInfo]:
    datasets = aquarius_datasets()
    datasets = pd.DataFrame(datasets[datasets["loc_id"] == station_id][["param", "label", "wp_dset_id"]]).rename(columns={"wp_dset_id": "id"})
    datasets = datasets.to_dict(orient="records")
    return {f"{dataset['param']}@{dataset['label']}": dataset for dataset in datasets}  # type: ignore


if __name__ == "__main__":
    import time
    from pprint import pprint

    start = time.time()
    datasets = station_datasets("29037020")
    end = time.time()
    print(f"Time taken: {end - start} seconds")
    pprint(datasets)
