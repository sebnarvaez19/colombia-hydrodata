import functools
import time
from dataclasses import dataclass
from pprint import pprint

import pandas as pd
from aquarius_webportal import AquariusWebPortal

wp = AquariusWebPortal("http://aquariuswebportal.ideam.gov.co/")


@dataclass
class Variable:
    param: str
    label: str
    id: int

    def fetch(self):
        return "fetching..."


def list_variables(df: pd.DataFrame) -> list[Variable]:
    df_d = df[["param", "label", "wp_dset_id"]]
    vars = []
    for _, row in df_d.iterrows():
        vars.append(Variable(param=row["param"], label=row["label"], id=row["wp_dset_id"]))  # type: ignore
    return vars


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} took {elapsed:0.2f} seconds")
        return result

    return wrapper


@timer
def fetch_datasets(station_id: str):
    datasets = []
    for param in wp.fetch_params()["param_name"]:
        datasets.append(wp.fetch_datasets(param_name=param))
    datasets = pd.concat(datasets, ignore_index=True)
    datasets.to_excel("./datasets.xlsx")
    data = pd.DataFrame(datasets[datasets["loc_id"] == station_id])
    vars = list_variables(data)
    return vars


if __name__ == "__main__":
    pprint(fetch_datasets("29037020"))
