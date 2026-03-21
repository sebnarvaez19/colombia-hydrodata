from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

import pandas as pd

from colombia_hydrodata.attributes import Variable
from colombia_hydrodata.utils.fetch.aquarius import dataset

if TYPE_CHECKING:
    from colombia_hydrodata.station import Station


@dataclass
class Dataset:
    station: "Station"
    variable: Variable
    data: pd.DataFrame

    @classmethod
    def from_variable(cls, station: "Station", variable: Variable) -> Self:
        return cls(station, variable, dataset(variable.id))
