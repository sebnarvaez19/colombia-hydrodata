import pandas as pd
from keys import cne_names

numeric_fields = ["altitud", "latitud", "longitud"]
date_fields = ["fecha_instalacion", "fecha_suspension"]


def transform_stations_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["nombre"] = df["nombre"].map(lambda x: x.split(" [")[0])
    for field in numeric_fields:
        df[field] = pd.to_numeric(df[field], errors="coerce")
    for field in date_fields:
        df[field] = pd.to_datetime(df[field], errors="coerce")

    return pd.DataFrame(df.rename(columns=cne_names)[list(cne_names.values())])
